import time
import picamera
import numpy as np
import cv2
import bot


image_width = 64
image_height = 32


channel = 0
init_wait = 0


front_control = bot.FrontControl()
rear_control = bot.RearControl()



while True:

	with picamera.PiCamera() as camera:
		camera.resolution = (image_width, image_height)
		camera.framerate = 15
		#time.sleep(2)

		#capture

		color_img = np.empty((image_height * image_width * 3,), dtype=np.uint8)
		camera.capture(color_img, 'bgr')
		color_img = color_img.reshape((image_height, image_width, 3))

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

		

		#cv2.imwrite( "0.jpg", tri_channel_turple[0]);

		#cv2.imwrite( "1.jpg", tri_channel_turple[1]);

		#cv2.imwrite( "2.jpg", tri_channel_turple[2]);

		

		print("OK")

		channel = 0

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
		if white_count/top_count > 0.2: #this is a turn
			white_center = np.sum(white_index)/white_count
			if white_center>image_width/2:
				#right

				front_control.change_angle(1.0)
				rear_control.set_speed(0.7)

				time.sleep(3)
				front_control.change_angle(0.5)
				rear_control.set_speed(0.3)

			else:

				#left
				pass



		if white_count == 0:
			white_count = 1

		white_center = np.sum(white_index)/white_count
		angle = (white_center+center_mod)/image_width
		print(angle)

		if angle > 0.7:
			angle = 0.7

		elif angle < 0.3:
			angle = 0.3

		front_control.change_angle(angle)

		if init_wait < 2:
			init_wait += 1

		else:
			rear_control.set_speed(0.3)

			#if angle > 0.7 or angle < 0.3:

			#	rear_control.set_speed(0.5)

			#else:

			#	rear_control.set_speed(0.3)

		

	#time.sleep(1)

