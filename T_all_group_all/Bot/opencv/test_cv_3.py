import numpy as np
import cv2

image_file = 'image1.png'

image_width = 640
image_height = 320

color_img = cv2.imread(image_file,cv2.IMREAD_COLOR)

# resize
color_img = cv2.resize(color_img, (image_width, image_height), interpolation=cv2.INTER_CUBIC)

# rotate
rows,cols,channel = color_img.shape
M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
color_img = cv2.warpAffine(color_img,M,(cols,rows))

#cut

#color_img = color_img[int(0.1*image_height):image_height]


#image_height, image_width, c =color_img.shape

#top_block = color_img[int(0.1*image_height):int(0.3*image_height)]
#sub_block = color_img[int(0.3*image_height):int(0.4*image_height)]
#mid_block = color_img[int(0.4*image_height):int(0.7*image_height)]

#cv2.imshow("TOP",top_block)
#cv2.imshow("SUB",sub_block)
#cv2.imshow("MID",mid_block)

# finish pre processing

gray_img = cv2.cvtColor(color_img,cv2.COLOR_RGB2GRAY)

# gray to binary

retval, binary_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_OTSU)

#print(binary_img)

cv2.imshow("Color",color_img)
#cv2.imshow("Gray",gray_img)
#cv2.imshow("Binary",binary_img)

inv_binary_img = cv2.bitwise_not(binary_img)

tri_binary = cv2.merge([inv_binary_img, inv_binary_img, inv_binary_img])

#filted_color = color_img.copy()
#

filted_color = cv2.bitwise_and(color_img,tri_binary)
		
cv2.imshow("FC",filted_color)


#(B,G,R) = cv2.split(filted_color)
tri_channel_turple = cv2.split(filted_color)


channel = 0

#channel_threshold = 100
#channel_threshold = [0,0,0]
#channel_threshold[0] = 100 #B
#channel_threshold[1] = 100 #G
#channel_threshold[2] = 180 #R



for i in range(image_height):
	for j in range(image_width):
		#print(filted_color[i,j])
		if (filted_color[i,j] != [0,0,0]).all():
			
			sort_index = np.argsort(-filted_color[i,j])

			
			tri_channel_turple[sort_index[0]][i,j]=255
			tri_channel_turple[sort_index[1]][i,j]=0
			tri_channel_turple[sort_index[2]][i,j]=0


for channel in range(3):

	#retval, channel_binary = cv2.threshold(tri_channel_turple[channel],channel_threshold[channel],255,cv2.THRESH_BINARY)
	cv2.imshow("channel"+str(channel),tri_channel_turple[channel])

channel = 0

top_block = tri_channel_turple[channel][int(0.1*image_height):int(0.3*image_height)]

#sub_block = color_img[int(0.3*image_height):int(0.4*image_height)]
#mid_block = color_img[int(0.4*image_height):int(0.7*image_height)]

center_mod = 0

print(top_block)

white_count = np.sum(top_block == 255)
white_index = np.where(top_block == 255)


if white_count == 0:
	white_count = 1

		

white_center = np.sum(white_index)/white_count
angle = (white_center+center_mod)/image_width
print(angle)


cv2.waitKey(0)
cv2.destroyAllWindows()