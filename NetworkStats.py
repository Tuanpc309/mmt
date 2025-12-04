import time
import threading

class NetworkStats:
	"""Track network statistics for video streaming."""
	
	def __init__(self):
		self.lock = threading.Lock()
		self.reset()
		
	def reset(self):
		"""Reset all statistics."""
		with self.lock:
			self.totalPacketsSent = 0
			self.totalPacketsReceived = 0
			self.totalBytesSent = 0
			self.totalBytesReceived = 0
			self.packetsLost = 0
			self.framesSent = 0
			self.framesReceived = 0
			self.framesLost = 0
			self.fragmentsSent = 0
			self.fragmentsReceived = 0
			self.startTime = time.time()
			self.lastPacketTime = time.time()
			self.latencies = []
			self.jitters = []
			self.lastArrivalTime = None
			self.lastTransitTime = None
			
	def recordPacketSent(self, packetSize):
		"""Record a sent packet."""
		with self.lock:
			self.totalPacketsSent += 1
			self.totalBytesSent += packetSize
			self.lastPacketTime = time.time()
	
	def recordFragmentSent(self):
		"""Record a sent fragment."""
		with self.lock:
			self.fragmentsSent += 1
			
	def recordFrameSent(self):
		"""Record a sent frame."""
		with self.lock:
			self.framesSent += 1
	
	def recordPacketReceived(self, packetSize, timestamp=None):
		"""Record a received packet."""
		with self.lock:
			self.totalPacketsReceived += 1
			self.totalBytesReceived += packetSize
			
			# Calculate latency if timestamp provided
			if timestamp:
				latency = (time.time() - timestamp) * 1000  # Convert to ms
				self.latencies.append(latency)
				
				# Calculate jitter (variation in latency)
				if self.lastArrivalTime is not None:
					arrivalDelta = time.time() - self.lastArrivalTime
					if self.lastTransitTime is not None:
						transitDelta = timestamp - self.lastTransitTime
						jitter = abs(arrivalDelta - transitDelta) * 1000  # ms
						self.jitters.append(jitter)
					self.lastTransitTime = timestamp
				
				self.lastArrivalTime = time.time()
	
	def recordFragmentReceived(self):
		"""Record a received fragment."""
		with self.lock:
			self.fragmentsReceived += 1
			
	def recordFrameReceived(self):
		"""Record a received frame."""
		with self.lock:
			self.framesReceived += 1
	
	def recordPacketLost(self):
		"""Record a lost packet."""
		with self.lock:
			self.packetsLost += 1
	
	def recordFrameLost(self):
		"""Record a lost frame."""
		with self.lock:
			self.framesLost += 1
	
	def getStats(self):
		"""Get current statistics as a dictionary."""
		with self.lock:
			elapsedTime = time.time() - self.startTime
			
			stats = {
				'packets_sent': self.totalPacketsSent,
				'packets_received': self.totalPacketsReceived,
				'packets_lost': self.packetsLost,
				'bytes_sent': self.totalBytesSent,
				'bytes_received': self.totalBytesReceived,
				'frames_sent': self.framesSent,
				'frames_received': self.framesReceived,
				'frames_lost': self.framesLost,
				'fragments_sent': self.fragmentsSent,
				'fragments_received': self.fragmentsReceived,
				'elapsed_time': elapsedTime,
				'bandwidth_sent_kbps': (self.totalBytesSent * 8 / 1024 / elapsedTime) if elapsedTime > 0 else 0,
				'bandwidth_received_kbps': (self.totalBytesReceived * 8 / 1024 / elapsedTime) if elapsedTime > 0 else 0,
				'packet_loss_rate': (self.packetsLost / (self.totalPacketsSent if self.totalPacketsSent > 0 else 1)) * 100,
				'frame_loss_rate': (self.framesLost / (self.framesSent if self.framesSent > 0 else 1)) * 100,
				'avg_latency_ms': (sum(self.latencies) / len(self.latencies)) if self.latencies else 0,
				'avg_jitter_ms': (sum(self.jitters) / len(self.jitters)) if self.jitters else 0,
			}
			
			return stats
	
	def printStats(self):
		"""Print statistics to console."""
		stats = self.getStats()
		print("\n" + "="*60)
		print("NETWORK STATISTICS")
		print("="*60)
		print(f"Elapsed Time: {stats['elapsed_time']:.2f} seconds")
		print(f"\nPackets:")
		print(f"  Sent: {stats['packets_sent']}")
		print(f"  Received: {stats['packets_received']}")
		print(f"  Lost: {stats['packets_lost']}")
		print(f"  Loss Rate: {stats['packet_loss_rate']:.2f}%")
		print(f"\nFrames:")
		print(f"  Sent: {stats['frames_sent']}")
		print(f"  Received: {stats['frames_received']}")
		print(f"  Lost: {stats['frames_lost']}")
		print(f"  Loss Rate: {stats['frame_loss_rate']:.2f}%")
		print(f"\nFragments:")
		print(f"  Sent: {stats['fragments_sent']}")
		print(f"  Received: {stats['fragments_received']}")
		print(f"\nBandwidth:")
		print(f"  Sent: {stats['bandwidth_sent_kbps']:.2f} Kbps")
		print(f"  Received: {stats['bandwidth_received_kbps']:.2f} Kbps")
		print(f"\nLatency:")
		print(f"  Average: {stats['avg_latency_ms']:.2f} ms")
		print(f"  Jitter: {stats['avg_jitter_ms']:.2f} ms")
		print("="*60 + "\n")
	
	def getStatsString(self):
		"""Get statistics as a formatted string."""
		stats = self.getStats()
		return (
			f"FPS: {stats['frames_received']}/{stats['elapsed_time']:.1f}s | "
			f"Loss: {stats['frame_loss_rate']:.1f}% | "
			f"BW: {stats['bandwidth_received_kbps']:.0f} Kbps | "
			f"Latency: {stats['avg_latency_ms']:.1f}ms"
		)
