import threading
import queue
import time
import cv2

class CVThread(threading.Thread):
	
	daemon = True
	index = 0
	image_queue = queue.Queue()
	
	def __init__(self):
		threading.Thread.__init__(self)
		
	def run(self):
		while True:

			ip, image = self.image_queue.get()
			print("RECEIVE IMAGE FROM " + str(ip))

			#cv2.imwrite('test_'+str(self.index)+'.png',image)
			self.index += 1
			self.image_queue.task_done()
		
	def put_image(self,image):
		self.image_queue.put(image)
		
