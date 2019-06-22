import threading
import queue
import time
import cv2
import numpy as np


class CVThread(threading.Thread):
	
	daemon = True
	index = 0
	image_queue = queue.Queue()
	
	def __init__(self):
		threading.Thread.__init__(self)
		
	def run(self):
		while True:

			ip, image, channel= self.image_queue.get()
			#print("RECEIVE IMAGE FROM " + str(ip))
			turn = self.handle_image(ip,image,channel)
			#cv2.imwrite('test_'+str(self.index)+'.png',image)
			self.index += 1
			self.image_queue.task_done()
			if turn:
				#pass
				self.image_queue.get()
				self.image_queue.task_done()
				#self.image_queue.get()
				#self.image_queue.task_done()
	
	def handle_image(self, ip, image, channel):
		color_img = image
		
		image_height, image_width, c = image.shape
	
		#rotate
		rows,cols,c = color_img.shape
		M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
		color_img = cv2.warpAffine(color_img,M,(cols,rows))
		
		#gray & gray binary
		gray_img = cv2.cvtColor(color_img,cv2.COLOR_RGB2GRAY)
		retval, binary_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_OTSU)
		inv_binary_img = cv2.bitwise_not(binary_img)
		tri_binary = cv2.merge([inv_binary_img, inv_binary_img, inv_binary_img])

		#cut floor
		filted_color = cv2.bitwise_and(color_img,tri_binary)

		#split channel
		tri_channel_turple = cv2.split(filted_color)

		
		for i in range(image_height):
			for j in range(image_width):
				if (filted_color[i,j] != [0,0,0]).all():
					sort_index = np.argsort(-filted_color[i,j])
					tri_channel_turple[sort_index[0]][i,j]=255
					tri_channel_turple[sort_index[1]][i,j]=0
					tri_channel_turple[sort_index[2]][i,j]=0

					

		#already get seprated tri channel image_height

		#cv2.imwrite("0.jpg", tri_channel_turple[0]);
		#cv2.imwrite("1.jpg", tri_channel_turple[1]);
		#cv2.imwrite("2.jpg", tri_channel_turple[2]);

		#print("OK")
		result_dict = {}
		
		# follow line
		
		

		top_block = tri_channel_turple[channel][int(0.0*image_height):int(0.2*image_height)]

		top_h, top_w = top_block.shape

		top_count = top_h * top_w

		#sub_block = color_img[int(0.3*image_height):int(0.4*image_height)]
		#mid_block = color_img[int(0.4*image_height):int(0.7*image_height)]

		center_mod = 5

		#print(top_block)

		white_count = np.sum(top_block == 255)
		white_index = np.where(top_block == 255)

		#print(white_count)
		print(white_count/top_count)
		if white_count/top_count > 0.20: #this is a turn
			result_dict['T'] = 1
			
		#	white_center = np.sum(white_index)/white_count
		#	if white_center>image_width/2:
		#		front_control.change_angle(1.0)
		#		rear_control.set_speed(0.7)
		#		time.sleep(3)
		#		front_control.change_angle(0.5)
		#		rear_control.set_speed(0.3)
		#	else:
		#		pass
		#	self.send_command(ip,{'A': 1.0, 'S': 0.7})
		#	time.sleep(1)
		#	self.send_command(ip,{'A': 0.5, 'S': 0.3})
		#	return

			

		if white_count == 0:
			white_count = 1

		white_center = np.sum(white_index)/white_count
		angle = (white_center+center_mod)/image_width
		#print(angle)

		if angle > 0.7:
			angle = 0.7

		elif angle < 0.3:
			angle = 0.3
		
		result_dict['A'] = angle
		
		self.send_result(ip,result_dict)
		
		if result_dict.get('T'):
			return True
		else:
			return False
		
		#front_control.change_angle(angle)
		
	def send_result(self,ip,result):
		pass
	
	def put_image(self,image):
		self.image_queue.put(image)

		
