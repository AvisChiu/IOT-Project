import time
import picamera
import numpy as np
import cv2
import bot



image_width = 320
image_height = 240



front_control = bot.FrontControl()
rear_control = bot.RearControl()



while True:

	with picamera.PiCamera() as camera:
		camera.resolution = (image_width, image_height)
		camera.framerate = 15

		#time.sleep(2)

		image = np.empty((image_height * image_width * 3,), dtype=np.uint8)
		camera.capture(image, 'bgr')
		image = image.reshape((image_height, image_width, 3))

		image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)

		#print(image.shape)

		# rotate

		rows,cols = image.shape
		M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
		img = cv2.warpAffine(image,M,(cols,rows))

		# binary
		retval, dst = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
		edge_cut = 10

		color = dst[1:10, edge_cut:image_width-edge_cut]
		center_mod = 15

		print("")

		try:
			black_count = np.sum(color == 0)
			black_index = np.where(color == 0)
			center = np.sum(black_index)/black_count
			print(center)
			direction = center - image_width/2
			print(direction)
			turn = (image_width/2 - center)/image_width
			print(turn)
			angle = (center+center_mod)/image_width
			print(angle)

			front_control.change_angle(angle)
			rear_control.set_speed(0.3)

		except Exception as e:
			print(e)
			
	#time.sleep(1)
