import sys
from time import time
HEADER_SIZE = 12
FRAGMENT_HEADER_SIZE = 4  # Fragment header: fragment_id(2) + total_fragments(1) + fragment_index(1)

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		self.fragmentHeader = None
		
	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload, fragment_id=0, total_fragments=1, fragment_index=0):
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())
		self.header = bytearray(HEADER_SIZE)
		
		# Fill the header bytearray with RTP header fields
		# Byte 0: V(2), P(1), X(1), CC(4)
		self.header[0] = (version << 6) | (padding << 5) | (extension << 4) | cc
		
		# Byte 1: M(1), PT(7)
		self.header[1] = (marker << 7) | pt
		
		# Bytes 2-3: Sequence number
		self.header[2] = (seqnum >> 8) & 0xFF
		self.header[3] = seqnum & 0xFF
		
		# Bytes 4-7: Timestamp
		self.header[4] = (timestamp >> 24) & 0xFF
		self.header[5] = (timestamp >> 16) & 0xFF
		self.header[6] = (timestamp >> 8) & 0xFF
		self.header[7] = timestamp & 0xFF
		
		# Bytes 8-11: SSRC
		self.header[8] = (ssrc >> 24) & 0xFF
		self.header[9] = (ssrc >> 16) & 0xFF
		self.header[10] = (ssrc >> 8) & 0xFF
		self.header[11] = ssrc & 0xFF
		
		# Add fragmentation header if this is a fragmented packet
		if total_fragments > 1:
			self.fragmentHeader = bytearray(FRAGMENT_HEADER_SIZE)
			self.fragmentHeader[0] = (fragment_id >> 8) & 0xFF
			self.fragmentHeader[1] = fragment_id & 0xFF
			self.fragmentHeader[2] = total_fragments & 0xFF
			self.fragmentHeader[3] = fragment_index & 0xFF
		else:
			self.fragmentHeader = None
		
		# Get the payload from the argument
		self.payload = payload
		
	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		
		# Check if fragmentation header exists (marker bit indicates fragmentation)
		remainingData = byteStream[HEADER_SIZE:]
		
		# Simple heuristic: if data starts with potential fragment header pattern
		# We check if the first 4 bytes could be a fragment header
		if len(remainingData) >= FRAGMENT_HEADER_SIZE:
			# Try to detect fragment header - fragment_id should be reasonable
			potential_frag_id = (remainingData[0] << 8) | remainingData[1]
			potential_total = remainingData[2]
			potential_index = remainingData[3]
			
			# If values suggest fragmentation (total > 1 and index < total)
			if potential_total > 1 and potential_index < potential_total and potential_frag_id < 100000:
				self.fragmentHeader = bytearray(remainingData[:FRAGMENT_HEADER_SIZE])
				self.payload = remainingData[FRAGMENT_HEADER_SIZE:]
			else:
				self.fragmentHeader = None
				self.payload = remainingData
		else:
			self.fragmentHeader = None
			self.payload = remainingData
	
	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def seqNum(self):
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)
	
	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		"""Return RTP packet."""
		if self.fragmentHeader:
			return self.header + self.fragmentHeader + self.payload
		return self.header + self.payload
	
	def isFragmented(self):
		"""Check if this packet is part of a fragmented frame."""
		return self.fragmentHeader is not None
	
	def getFragmentId(self):
		"""Return fragment ID."""
		if self.fragmentHeader:
			return (self.fragmentHeader[0] << 8) | self.fragmentHeader[1]
		return 0
	
	def getTotalFragments(self):
		"""Return total number of fragments."""
		if self.fragmentHeader:
			return self.fragmentHeader[2]
		return 1
	
	def getFragmentIndex(self):
		"""Return fragment index."""
		if self.fragmentHeader:
			return self.fragmentHeader[3]
		return 0