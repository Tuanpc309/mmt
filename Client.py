# from tkinter import *
# import tkinter.messagebox
# from PIL import Image, ImageTk
# import socket, threading, sys, traceback, os

# from RtpPacket import RtpPacket

# CACHE_FILE_NAME = "cache-"
# CACHE_FILE_EXT = ".jpg"

# class Client:
# 	INIT = 0
# 	READY = 1
# 	PLAYING = 2
# 	state = INIT
	
# 	SETUP = 0
# 	PLAY = 1
# 	PAUSE = 2
# 	TEARDOWN = 3
	
# 	# Initiation..
# 	def __init__(self, master, serveraddr, serverport, rtpport, filename):
# 		self.master = master
# 		self.master.protocol("WM_DELETE_WINDOW", self.handler)
# 		self.createWidgets()
# 		self.serverAddr = serveraddr
# 		self.serverPort = int(serverport)
# 		self.rtpPort = int(rtpport)
# 		self.fileName = filename
# 		self.rtspSeq = 0
# 		self.sessionId = 0
# 		self.requestSent = -1
# 		self.teardownAcked = 0
# 		self.connectToServer()
# 		self.frameNbr = 0
		
# 	def createWidgets(self):
# 		"""Build GUI."""
# 		# Create Setup button
# 		self.setup = Button(self.master, width=20, padx=3, pady=3)
# 		self.setup["text"] = "Setup"
# 		self.setup["command"] = self.setupMovie
# 		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
# 		# Create Play button		
# 		self.start = Button(self.master, width=20, padx=3, pady=3)
# 		self.start["text"] = "Play"
# 		self.start["command"] = self.playMovie
# 		self.start.grid(row=1, column=1, padx=2, pady=2)
		
# 		# Create Pause button			
# 		self.pause = Button(self.master, width=20, padx=3, pady=3)
# 		self.pause["text"] = "Pause"
# 		self.pause["command"] = self.pauseMovie
# 		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
# 		# Create Teardown button
# 		self.teardown = Button(self.master, width=20, padx=3, pady=3)
# 		self.teardown["text"] = "Teardown"
# 		self.teardown["command"] =  self.exitClient
# 		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
# 		# Create a label to display the movie
# 		self.label = Label(self.master, height=19)
# 		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
# 	def setupMovie(self):
# 		"""Setup button handler."""
# 		if self.state == self.INIT:
# 			self.sendRtspRequest(self.SETUP)
	
# 	def exitClient(self):
# 		"""Teardown button handler."""
# 		self.sendRtspRequest(self.TEARDOWN)		
# 		self.master.destroy() # Close the gui window
# 		# Try remove cache file if exists
# 		try:
# 			os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT)
# 		except:
# 			pass

# 	def pauseMovie(self):
# 		"""Pause button handler."""
# 		if self.state == self.PLAYING:
# 			self.sendRtspRequest(self.PAUSE)
	
# 	def playMovie(self):
# 		"""Play button handler."""
# 		if self.state == self.READY:
# 			# Create a new thread to listen for RTP packets
# 			threading.Thread(target=self.listenRtp).start()
# 			self.playEvent = threading.Event()
# 			self.playEvent.clear()
# 			self.sendRtspRequest(self.PLAY)
	
# 	def listenRtp(self):		
# 		"""Listen for RTP packets."""
# 		while True:
# 			try:
# 				data = self.rtpSocket.recv(20480)
# 				if data:
# 					rtpPacket = RtpPacket()
# 					rtpPacket.decode(data)
					
# 					currFrameNbr = rtpPacket.seqNum()
# 					print("Current Seq Num: " + str(currFrameNbr))
										
# 					if currFrameNbr > self.frameNbr: # Discard the late packet
# 						self.frameNbr = currFrameNbr
# 						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
# 			except:
# 				# Stop listening upon requesting PAUSE or TEARDOWN
# 				if hasattr(self, 'playEvent') and self.playEvent.isSet(): 
# 					break
				
# 				# Upon receiving ACK for TEARDOWN request,
# 				# close the RTP socket
# 				if self.teardownAcked == 1:
# 					try:
# 						self.rtpSocket.shutdown(socket.SHUT_RDWR)
# 					except:
# 						pass
# 					try:
# 						self.rtpSocket.close()
# 					except:
# 						pass
# 					break
					
# 	def writeFrame(self, data):
# 		"""Write the received frame to a temp image file. Return the image file."""
# 		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
# 		file = open(cachename, "wb")
# 		file.write(data)
# 		file.close()
		
# 		return cachename
	
# 	def updateMovie(self, imageFile):
# 		"""Update the image file as video frame in the GUI."""
# 		photo = ImageTk.PhotoImage(Image.open(imageFile))
# 		self.label.configure(image = photo, height=288) 
# 		self.label.image = photo
		
# 	def connectToServer(self):
# 		"""Connect to the Server. Start a new RTSP/TCP session."""
# 		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 		try:
# 			self.rtspSocket.connect((self.serverAddr, self.serverPort))
# 		except:
# 			tkinter.messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
# 	def sendRtspRequest(self, requestCode):
# 		"""Send RTSP request to the server."""	
# 		#-------------
# 		# Complete implementation
# 		#-------------
		
# 		# Setup request
# 		if requestCode == self.SETUP and self.state == self.INIT:
# 			# start thread to receive RTSP replies
# 			threading.Thread(target=self.recvRtspReply).start()
# 			# Update RTSP sequence number.
# 			self.rtspSeq += 1
			
# 			# Write the RTSP request to be sent.
# 			# Format: SETUP filename RTSP/1.0
# 			# CSeq: <seq>
# 			# Transport: RTP/UDP; client_port= <rtpPort>
# 			request = (f"SETUP {self.fileName} RTSP/1.0\r\n" +
# 					   f"CSeq: {self.rtspSeq}\r\n" +
# 					   f"Transport: RTP/UDP; client_port= {self.rtpPort}\r\n\r\n")
			
# 			# Keep track of the sent request.
# 			self.requestSent = self.SETUP
		
# 		# Play request
# 		elif requestCode == self.PLAY and self.state == self.READY:
# 			# Update RTSP sequence number.
# 			self.rtspSeq += 1
			
# 			# Write the RTSP request to be sent.
# 			# Include Session header
# 			request = (f"PLAY {self.fileName} RTSP/1.0\r\n" +
# 					   f"CSeq: {self.rtspSeq}\r\n" +
# 					   f"Session: {self.sessionId}\r\n\r\n")
			
# 			# Keep track of the sent request.
# 			self.requestSent = self.PLAY
		
# 		# Pause request
# 		elif requestCode == self.PAUSE and self.state == self.PLAYING:
# 			# Update RTSP sequence number.
# 			self.rtspSeq += 1
			
# 			# Write the RTSP request to be sent.
# 			request = (f"PAUSE {self.fileName} RTSP/1.0\r\n" +
# 					   f"CSeq: {self.rtspSeq}\r\n" +
# 					   f"Session: {self.sessionId}\r\n\r\n")
			
# 			# Keep track of the sent request.
# 			self.requestSent = self.PAUSE
			
# 		# Teardown request
# 		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
# 			# Update RTSP sequence number.
# 			self.rtspSeq += 1
			
# 			# Write the RTSP request to be sent.
# 			request = (f"TEARDOWN {self.fileName} RTSP/1.0\r\n" +
# 					   f"CSeq: {self.rtspSeq}\r\n" +
# 					   f"Session: {self.sessionId}\r\n\r\n")
			
# 			# Keep track of the sent request.
# 			self.requestSent = self.TEARDOWN
# 		else:
# 			# invalid request for current state
# 			return
		
# 		# Send the RTSP request using rtspSocket.
# 		try:
# 			self.rtspSocket.send(request.encode())
# 		except Exception as e:
# 			print("Failed to send RTSP request:", e)
# 			tkinter.messagebox.showwarning('Send Failed', 'Failed to send RTSP request.')
# 			return
		
# 		print('\nData sent:\n' + request)
	
# 	def recvRtspReply(self):
# 		"""Receive RTSP reply from the server."""
# 		while True:
# 			reply = self.rtspSocket.recv(1024)
			
# 			if reply: 
# 				self.parseRtspReply(reply.decode("utf-8"))
			
# 			# Close the RTSP socket upon requesting Teardown
# 			if self.requestSent == self.TEARDOWN:
# 				try:
# 					self.rtspSocket.shutdown(socket.SHUT_RDWR)
# 				except:
# 					pass
# 				try:
# 					self.rtspSocket.close()
# 				except:
# 					pass
# 				break
	
# 	def parseRtspReply(self, data):
# 		"""Parse the RTSP reply from the server."""
# 		lines = data.split('\n')
# 		# Expecting lines like:
# 		# RTSP/1.0 200 OK
# 		# CSeq: <num>
# 		# Session: <id>
# 		# ...
# 		try:
# 			seqNum = int(lines[1].split(' ')[1])
# 		except:
# 			print("Bad RTSP reply (no CSeq):", data)
# 			return
		
# 		# Process only if the server reply's sequence number is the same as the request's
# 		if seqNum == self.rtspSeq:
# 			try:
# 				session = int(lines[2].split(' ')[1])
# 			except:
# 				session = 0
# 			# New RTSP session ID
# 			if self.sessionId == 0:
# 				self.sessionId = session
			
# 			# Process only if the session ID is the same
# 			if self.sessionId == session or self.sessionId == 0:
# 				try:
# 					status_code = int(lines[0].split(' ')[1])
# 				except:
# 					status_code = 0
# 				if status_code == 200: 
# 					if self.requestSent == self.SETUP:
# 						# Update RTSP state.
# 						self.state = self.READY
						
# 						# Open RTP port.
# 						self.openRtpPort() 
# 					elif self.requestSent == self.PLAY:
# 						self.state = self.PLAYING
# 					elif self.requestSent == self.PAUSE:
# 						self.state = self.READY
						
# 						# The play thread exits. A new thread is created on resume.
# 						if hasattr(self, 'playEvent'):
# 							self.playEvent.set()
# 					elif self.requestSent == self.TEARDOWN:
# 						self.state = self.INIT
						
# 						# Flag the teardownAcked to close the socket.
# 						self.teardownAcked = 1 
	
# 	def openRtpPort(self):
# 		"""Open RTP socket binded to a specified port."""
# 		#-------------
# 		# Create a new datagram socket to receive RTP packets from the server
# 		#-------------
# 		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
# 		# Set the timeout value of the socket to 0.5sec
# 		self.rtpSocket.settimeout(0.5)
		
# 		try:
# 			# Bind the socket to the address using the RTP port given by the client user
# 			self.rtpSocket.bind(('', self.rtpPort))
# 			print("Bind RTP on port", self.rtpPort)
# 		except Exception as e:
# 			tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d\n%s' %(self.rtpPort, str(e)))
# 			return

# 	def handler(self):
# 		"""Handler on explicitly closing the GUI window."""
# 		self.pauseMovie()
# 		if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
# 			self.exitClient()
# 		else: # When the user presses cancel, resume playing.
# 			self.playMovie()


#file tao

from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import io       # Thư viện xử lý RAM
import queue    # Thư viện hàng đợi

from RtpPacket import RtpPacket

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
    
    # [Cấu hình Buffer]
    # Khi mới bấm Play, Client sẽ chờ tích đủ số lượng ảnh này rồi mới bắt đầu chiếu.
    # Giúp video không bị giật nếu mạng chập chờn lúc đầu.
    BUFFER_THRESHOLD = 50
    
    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
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
        
        # Hàng đợi Buffer
        self.frameBuffer = queue.Queue()
        # Cờ đánh dấu xem đã bắt đầu chiếu hay chưa (để xử lý pre-buffer)
        self.is_displaying = False 

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
        self.teardown["command"] = self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)
        
        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
    
    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)
    
    def exitClient(self):
        """Teardown button handler."""
        self.sendRtspRequest(self.TEARDOWN)     
        self.master.destroy() 

    def pauseMovie(self):
        """Pause button handler."""
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)
    
    def playMovie(self):
        """Play button handler."""
        if self.state == self.READY:
            # 1. Reset trạng thái
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.is_displaying = False # Reset cờ hiển thị để kích hoạt lại Buffer
            
            # 2. Tạo luồng nhận tin (Producer)
            threading.Thread(target=self.listenRtp).start()
            
            # 3. Kích hoạt luồng chiếu phim (Consumer)
            self.run_buffer_consumer()
            
            self.sendRtspRequest(self.PLAY)
    
    def run_buffer_consumer(self):
        """Hàm Consumer: Lấy ảnh từ Buffer ra chiếu."""
        if self.playEvent.isSet(): 
            return

        # --- LOGIC CACHING (PRE-BUFFERING) ---
        # Nếu chưa bắt đầu chiếu (lần đầu hoặc sau khi pause),
        # hãy kiểm tra xem kho đã đủ hàng (BUFFER_THRESHOLD) chưa.
        if not self.is_displaying:
            if self.frameBuffer.qsize() >= self.BUFFER_THRESHOLD:
                self.is_displaying = True # Đã đủ hàng, bắt đầu xả kho!
                print(f"[Buffer] Đã tích đủ {self.frameBuffer.qsize()} frame. Bắt đầu phát video!")
            else:
                # Nếu chưa đủ thì chưa làm gì cả, chỉ in ra log chơi thôi
                # print(f"Buffering... {self.frameBuffer.qsize()}/{self.BUFFER_THRESHOLD}")
                pass
        
        # Nếu đã ở trạng thái được phép chiếu (is_displaying = True)
        if self.is_displaying and not self.frameBuffer.empty():
            next_frame_data = self.frameBuffer.get()
            self.updateMovie(next_frame_data)
        
        # Gọi lại hàm này sau 40ms (Tăng tốc độ lên chút cho mượt, 40ms ~ 25 FPS)
        self.master.after(40, self.run_buffer_consumer)

    def listenRtp(self):        
        """Listen for RTP packets (Producer)."""
        while True:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)
                    
                    currFrameNbr = rtpPacket.seqNum()
                    
                    if currFrameNbr > self.frameNbr: 
                        self.frameNbr = currFrameNbr
                        
                        # Chỉ việc ném vào Buffer (Nhập kho)
                        frame_data = rtpPacket.getPayload()
                        self.frameBuffer.put(frame_data)
            except:
                if self.playEvent.isSet(): 
                    break
                if self.teardownAcked == 1:
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()
                    break
                    
    def updateMovie(self, frame_data):
        """Update the image file as video frame in the GUI."""
        try:
            # Đọc ảnh từ RAM
            image_stream = io.BytesIO(frame_data)
            photo = ImageTk.PhotoImage(Image.open(image_stream))
            
            self.label.configure(image = photo, height=288) 
            self.label.image = photo
        except Exception as e:
            print("Error updating movie frame: ", e)
        
    def connectToServer(self):
        """Connect to the Server."""
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
            self.rtspSeq += 1
            request = "SETUP " + str(self.fileName) + " RTSP/1.0\n"
            request += "CSeq: " + str(self.rtspSeq) + "\n"
            request += "Transport: RTP/UDP; client_port= " + str(self.rtpPort)
            self.requestSent = self.SETUP
        
        # Play request
        elif requestCode == self.PLAY and self.state == self.READY:
            self.rtspSeq += 1
            request = "PLAY " + str(self.fileName) + " RTSP/1.0\n"
            request += "CSeq: " + str(self.rtspSeq) + "\n"
            request += "Session: " + str(self.sessionId)
            self.requestSent = self.PLAY
        
        # Pause request
        elif requestCode == self.PAUSE and self.state == self.PLAYING:
            self.rtspSeq += 1
            request = "PAUSE " + str(self.fileName) + " RTSP/1.0\n"
            request += "CSeq: " + str(self.rtspSeq) + "\n"
            request += "Session: " + str(self.sessionId)
            self.requestSent = self.PAUSE
            
        # Teardown request
        elif requestCode == self.TEARDOWN and not self.state == self.INIT:
            self.rtspSeq += 1
            request = "TEARDOWN " + str(self.fileName) + " RTSP/1.0\n"
            request += "CSeq: " + str(self.rtspSeq) + "\n"
            request += "Session: " + str(self.sessionId)
            self.requestSent = self.TEARDOWN
        else:
            return
        
        self.rtspSocket.send(request.encode("utf-8"))
        print('\nData sent:\n' + request)
    
    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        while True:
            reply = self.rtspSocket.recv(1024)
            
            if reply: 
                self.parseRtspReply(reply.decode("utf-8"))
            
            if self.requestSent == self.TEARDOWN:
                self.rtspSocket.shutdown(socket.SHUT_RDWR)
                self.rtspSocket.close()
                break
    
    def parseRtspReply(self, data):
        """Parse the RTSP reply from the server."""
        lines = data.split('\n')
        seqNum = int(lines[1].split(' ')[1])
        
        if seqNum == self.rtspSeq:
            session = int(lines[2].split(' ')[1])
            if self.sessionId == 0:
                self.sessionId = session
            
            if self.sessionId == session:
                if int(lines[0].split(' ')[1]) == 200: 
                    if self.requestSent == self.SETUP:
                        self.state = self.READY
                        self.openRtpPort() 
                    elif self.requestSent == self.PLAY:
                        self.state = self.PLAYING
                    elif self.requestSent == self.PAUSE:
                        self.state = self.READY
                        self.playEvent.set()
                    elif self.requestSent == self.TEARDOWN:
                        self.state = self.INIT
                        self.teardownAcked = 1 
    
    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtpSocket.settimeout(0.5)
        try:
            self.state = self.READY
            self.rtpSocket.bind(("", self.rtpPort))
        except:
            tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()
        else:
            self.playMovie()




















