import cv2, numpy as np

class VideoStream():
	def __init__(self,filename):
		#self.filename = "utils/movie.Mjpeg"
		try:
			self.file = cv2.VideoCapture(filename)
			print("abriu o ficheiro")
		except:
			print("deu merda oh filho")
			raise IOError
		self.frameNum = 0
		
	def nextFrame(self):
		"""Get next frame."""
		ret, frame = self.file.read() # Get the framelength from the first 5 bits
		value ,jpeg_bytes = cv2.imencode('.jpg', frame)
		# jpeg_data = (jpeg_bytes).tobytes()
		if ret:
			self.frameNum += 1
			print(type(jpeg_bytes))	
			print(jpeg_bytes)	
			# jpeg_bytes -> (True, [bytes])
			data = (self.frameNum, jpeg_bytes)
		return data
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum