from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import time

from RtpPacket import RtpPacket
from NetworkStats import NetworkStats

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.title("HD Video Streaming Client - RTP")
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		
		# Configure window for HD video
		self.master.geometry("1200x750")
		self.master.resizable(True, True)
		
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		
		# Fragment reassembly buffers
		self.fragmentBuffer = {}  # {fragment_id: {fragment_index: data}}
		self.fragmentMetadata = {}  # {fragment_id: (total_fragments, frame_number)}
		
		# Network statistics
		self.stats = NetworkStats()
		self.lastStatsUpdate = time.time()
		
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie with better sizing for HD
		self.label = Label(self.master, bg="black")
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)
		
		# Create a label to display network statistics
		self.statsLabel = Label(self.master, text="Network Stats: Not started", bg="lightgray", anchor=W, font=('Arial', 10))
		self.statsLabel.grid(row=2, column=0, columnspan=4, sticky=W+E, padx=5, pady=2)
		
		# Configure grid weights for resizing
		self.master.grid_rowconfigure(0, weight=1)
		self.master.grid_columnconfigure(0, weight=1)
		self.master.grid_columnconfigure(1, weight=1)
		self.master.grid_columnconfigure(2, weight=1)
		self.master.grid_columnconfigure(3, weight=1) 
	
	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
		self.sendRtspRequest(self.TEARDOWN)		
		self.master.destroy() # Close the gui window
		os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			# Create a new thread to listen for RTP packets
			threading.Thread(target=self.listenRtp).start()
			self.playEvent = threading.Event()
			self.playEvent.clear()
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets with fragment reassembly support."""
		while True:
			try:
				data = self.rtpSocket.recv(65536)  # Increased buffer for HD
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)
					
					currFrameNbr = rtpPacket.seqNum()
					timestamp = rtpPacket.timestamp()
					
					# Record packet statistics
					self.stats.recordPacketReceived(len(data), timestamp)
					
					# Check if this is a fragmented packet
					if rtpPacket.isFragmented():
						# Handle fragmented frame
						self.handleFragmentedPacket(rtpPacket, currFrameNbr)
					else:
						# Handle complete frame
						if currFrameNbr > self.frameNbr:  # Discard late packets
							self.frameNbr = currFrameNbr
							self.stats.recordFrameReceived()
							self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
							print(f"[Client] Frame {currFrameNbr} received (complete)")
						else:
							print(f"[Client] Discarded late packet: {currFrameNbr}")
							self.stats.recordPacketLost()
					
					# Update statistics display every second
					if time.time() - self.lastStatsUpdate > 1.0:
						self.updateStatsDisplay()
						self.lastStatsUpdate = time.time()
						
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet(): 
					break
				
				# Upon receiving ACK for TEARDOWN request,
				# close the RTP socket
				if self.teardownAcked == 1:
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					break
		
		# Print final statistics
		print("\n[Client] Playback stopped. Final statistics:")
		self.stats.printStats()
	
	def handleFragmentedPacket(self, rtpPacket, frameNbr):
		"""Handle fragmented RTP packets and reassemble frames."""
		fragmentId = rtpPacket.getFragmentId()
		totalFragments = rtpPacket.getTotalFragments()
		fragmentIndex = rtpPacket.getFragmentIndex()
		
		self.stats.recordFragmentReceived()
		
		print(f"[Client] Received fragment {fragmentIndex+1}/{totalFragments} for frame {frameNbr} (frag_id: {fragmentId})")
		
		# Initialize buffer for this fragment ID if needed
		if fragmentId not in self.fragmentBuffer:
			self.fragmentBuffer[fragmentId] = {}
			self.fragmentMetadata[fragmentId] = (totalFragments, frameNbr)
		
		# Store the fragment
		self.fragmentBuffer[fragmentId][fragmentIndex] = rtpPacket.getPayload()
		
		# Check if we have all fragments
		if len(self.fragmentBuffer[fragmentId]) == totalFragments:
			# Reassemble the frame
			completeFrame = bytearray()
			for i in range(totalFragments):
				if i in self.fragmentBuffer[fragmentId]:
					completeFrame.extend(self.fragmentBuffer[fragmentId][i])
				else:
					print(f"[Client] Warning: Missing fragment {i} for frame {frameNbr}")
					self.stats.recordFrameLost()
					# Clean up incomplete frame
					del self.fragmentBuffer[fragmentId]
					del self.fragmentMetadata[fragmentId]
					return
			
			# Update frame display
			if frameNbr > self.frameNbr:
				self.frameNbr = frameNbr
				self.stats.recordFrameReceived()
				self.updateMovie(self.writeFrame(bytes(completeFrame)))
				print(f"[Client] Frame {frameNbr} reassembled from {totalFragments} fragments ({len(completeFrame)} bytes)")
			
			# Clean up buffer
			del self.fragmentBuffer[fragmentId]
			del self.fragmentMetadata[fragmentId]
			
			# Clean up old incomplete fragments (timeout after 10 fragment IDs)
			oldFragmentIds = [fid for fid in self.fragmentBuffer.keys() if fragmentId - fid > 10]
			for fid in oldFragmentIds:
				print(f"[Client] Cleaning up incomplete fragment {fid}")
				self.stats.recordFrameLost()
				del self.fragmentBuffer[fid]
				if fid in self.fragmentMetadata:
					del self.fragmentMetadata[fid]
	
	def updateStatsDisplay(self):
		"""Update the statistics label in the GUI."""
		statsStr = self.stats.getStatsString()
		self.statsLabel.config(text=statsStr)
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()
		
		return cachename
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI with smart scaling."""
		try:
			# Open image
			img = Image.open(imageFile)
			
			# Get current label size
			label_width = self.label.winfo_width()
			label_height = self.label.winfo_height()
			
			# Scale image to fit window while maintaining aspect ratio
			if label_width > 100 and label_height > 100:  # Valid size
				img_width, img_height = img.size
				aspect_ratio = img_width / img_height
				
				# Calculate best fit
				if label_width / label_height > aspect_ratio:
					# Height is limiting factor
					new_height = label_height
					new_width = int(new_height * aspect_ratio)
				else:
					# Width is limiting factor
					new_width = label_width
					new_height = int(new_width / aspect_ratio)
				
				# Resize image with high quality
				img = img.resize((new_width, new_height), Image.LANCZOS)
			
			# Convert to PhotoImage and display
			photo = ImageTk.PhotoImage(img)
			self.label.configure(image=photo)
			self.label.image = photo
			
		except Exception as e:
			print(f"[Client] Error updating display: {e}")
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		
		# Setup request
		if requestCode == self.SETUP and self.state == self.INIT:
			threading.Thread(target=self.recvRtspReply).start()
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = f"SETUP {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nTransport: RTP/UDP; client_port= {self.rtpPort}"
			
			# Keep track of the sent request.
			self.requestSent = self.SETUP
		
		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = f"PLAY {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}"
			
			# Keep track of the sent request.
			self.requestSent = self.PLAY
		
		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = f"PAUSE {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}"
			
			# Keep track of the sent request.
			self.requestSent = self.PAUSE
			
		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = f"TEARDOWN {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}"
			
			# Keep track of the sent request.
			self.requestSent = self.TEARDOWN
		else:
			return
		
		# Send the RTSP request using rtspSocket.
		self.rtspSocket.send(request.encode())
		
		print('\nData sent:\n' + request)
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		while True:
			reply = self.rtspSocket.recv(1024)
			
			if reply: 
				self.parseRtspReply(reply.decode("utf-8"))
			
			# Close the RTSP socket upon requesting Teardown
			if self.requestSent == self.TEARDOWN:
				self.rtspSocket.shutdown(socket.SHUT_RDWR)
				self.rtspSocket.close()
				break
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		lines = data.split('\n')
		seqNum = int(lines[1].split(' ')[1])
		
		# Process only if the server reply's sequence number is the same as the request's
		if seqNum == self.rtspSeq:
			session = int(lines[2].split(' ')[1])
			# New RTSP session ID
			if self.sessionId == 0:
				self.sessionId = session
			
			# Process only if the session ID is the same
			if self.sessionId == session:
				if int(lines[0].split(' ')[1]) == 200: 
					if self.requestSent == self.SETUP:
						# Update RTSP state.
						self.state = self.READY
						
						# Open RTP port.
						self.openRtpPort() 
					elif self.requestSent == self.PLAY:
						self.state = self.PLAYING
					elif self.requestSent == self.PAUSE:
						self.state = self.READY
						
						# The play thread exits. A new thread is created on resume.
						self.playEvent.set()
					elif self.requestSent == self.TEARDOWN:
						self.state = self.INIT
						
						# Flag the teardownAcked to close the socket.
						self.teardownAcked = 1 
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(0.5)
		
		try:
			# Bind the socket to the address using the RTP port given by the client user
			self.rtpSocket.bind(('', self.rtpPort))
		except:
			tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pauseMovie()
		if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
		else: # When the user presses cancel, resume playing.
			self.playMovie()
