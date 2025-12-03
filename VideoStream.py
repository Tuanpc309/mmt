class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		self.frameNum = 0
		self.frames = [] # Danh sách chứa các khung hình đã cắt
		self.load_frames() # Tự động cắt file ngay khi khởi động

	def load_frames(self):
		"""Đọc toàn bộ file và tách các khung hình dựa trên header JPEG."""
		try:
			with open(self.filename, 'rb') as file:
				data = file.read()
				
				# JPEG bắt đầu bằng 0xFF 0xD8 và kết thúc bằng 0xFF 0xD9
				start = 0
				while True:
					# Tìm điểm bắt đầu (SOI - Start of Image)
					start_pos = data.find(b'\xff\xd8', start)
					if start_pos == -1:
						break
					
					# Tìm điểm kết thúc (EOI - End of Image)
					end_pos = data.find(b'\xff\xd9', start_pos)
					if end_pos == -1:
						break
					
					# Trích xuất khung hình (cộng thêm 2 byte cuối FF D9)
					frame = data[start_pos:end_pos + 2]
					self.frames.append(frame)
					
					# Di chuyển con trỏ để tìm khung tiếp theo
					start = end_pos + 2
		except:
			print("Error loading video file.")
			raise IOError

	def nextFrame(self):
		"""Lấy khung hình tiếp theo từ danh sách đã tải."""
		if self.frameNum < len(self.frames):
			frame = self.frames[self.frameNum]
			self.frameNum += 1
			return frame
		return None
		
	def frameNbr(self):
		"""Lấy số thứ tự khung hình hiện tại."""
		return self.frameNum
