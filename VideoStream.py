class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		self.totalBytesRead = 0
		self.lastFrameSize = 0
		
		# Auto-detect file format
		self.fileFormat = self._detectFormat()
		print(f"[VideoStream] Detected format: {self.fileFormat}")
		
	def _detectFormat(self):
		"""Detect if file is custom format (with length prefix) or standard MJPEG."""
		pos = self.file.tell()
		firstBytes = self.file.read(5)
		self.file.seek(pos)
		
		if not firstBytes or len(firstBytes) < 5:
			return 'unknown'
		
		# Try to parse as custom format (5-digit decimal length)
		try:
			length = int(firstBytes)
			# If it's a reasonable length, likely custom format
			if 0 < length < 5000000:
				return 'custom'
		except:
			pass
		
		# Check for JPEG marker (FF D8)
		if firstBytes[0] == 0xFF and firstBytes[1] == 0xD8:
			return 'mjpeg'
		
		return 'custom'  # Default to custom format
		
	def nextFrame(self):
		"""Get next frame - supports both custom format and standard MJPEG."""
		if self.fileFormat == 'mjpeg':
			return self._nextFrameMJPEG()
		else:
			return self._nextFrameCustom()
	
	def _nextFrameCustom(self):
		"""Read frame from custom format (5-byte length prefix + data)."""
		try:
			# Read frame length (first 5 bytes as decimal string)
			lengthData = self.file.read(5)
			if not lengthData or len(lengthData) < 5:
				return None
				
			framelength = int(lengthData)
			
			# Validate frame length (sanity check for HD frames up to 5MB)
			if framelength <= 0 or framelength > 5000000:
				print(f"[VideoStream] Warning: Invalid frame length {framelength}, skipping")
				return None
							
			# Read the current frame data
			data = self.file.read(framelength)
			
			if len(data) == framelength:
				self.frameNum += 1
				self.lastFrameSize = framelength
				self.totalBytesRead += framelength + 5  # Include length prefix
				
				# Log large frames (HD frames)
				if framelength > 20000:  # > 20KB is likely HD
					print(f"[VideoStream] HD Frame {self.frameNum}: {framelength} bytes")
				
				return data
			else:
				print(f"[VideoStream] Warning: Expected {framelength} bytes, got {len(data)}")
				return None
				
		except ValueError as e:
			print(f"[VideoStream] Error reading frame length: {e}")
			return None
		except Exception as e:
			print(f"[VideoStream] Error reading frame: {e}")
			return None
	
	def _nextFrameMJPEG(self):
		"""Read frame from standard MJPEG format (JPEG markers)."""
		try:
			# Look for JPEG start marker (FF D8)
			frameData = bytearray()
			
			# Read until we find FF D8 (JPEG start)
			byte1 = self.file.read(1)
			if not byte1:
				return None
			
			# If we're not at a frame start, search for it
			if byte1[0] != 0xFF:
				while True:
					byte1 = self.file.read(1)
					if not byte1:
						return None
					if byte1[0] == 0xFF:
						break
			
			byte2 = self.file.read(1)
			if not byte2 or byte2[0] != 0xD8:
				print(f"[VideoStream] Warning: Expected JPEG marker, got {byte2.hex() if byte2 else 'EOF'}")
				return None
			
			# Start of JPEG frame
			frameData.extend(byte1)
			frameData.extend(byte2)
			
			# Read until we find JPEG end marker (FF D9)
			while True:
				byte = self.file.read(1)
				if not byte:
					# End of file
					if len(frameData) > 100:  # Minimum valid JPEG size
						break
					return None
				
				frameData.append(byte[0])
				
				# Check for end marker (FF D9)
				if len(frameData) >= 2 and frameData[-2] == 0xFF and frameData[-1] == 0xD9:
					break
				
				# Safety check - don't read frames larger than 5MB
				if len(frameData) > 5000000:
					print(f"[VideoStream] Warning: Frame exceeds 5MB, stopping read")
					break
			
			if len(frameData) > 100:  # Valid JPEG frame
				self.frameNum += 1
				self.lastFrameSize = len(frameData)
				self.totalBytesRead += len(frameData)
				
				# Log large frames (HD frames)
				if len(frameData) > 20000:
					print(f"[VideoStream] HD Frame {self.frameNum}: {len(frameData)} bytes")
				
				return bytes(frameData)
			else:
				return None
				
		except Exception as e:
			print(f"[VideoStream] Error reading MJPEG frame: {e}")
			return None
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
	
	def getLastFrameSize(self):
		"""Get the size of the last frame read."""
		return self.lastFrameSize
	
	def getTotalBytesRead(self):
		"""Get total bytes read from the video file."""
		return self.totalBytesRead
	
	def reset(self):
		"""Reset the video stream to the beginning."""
		self.file.seek(0)
		self.frameNum = 0
		self.totalBytesRead = 0
		self.lastFrameSize = 0
	
	