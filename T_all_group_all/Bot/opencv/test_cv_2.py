import numpy as np
import cv2

image_file = 'img0.png'

image_width = 1024
image_height = 768

color_img = cv2.imread(image_file,cv2.IMREAD_COLOR)

# resize
color_img = cv2.resize(color_img, (image_width, image_height), interpolation=cv2.INTER_CUBIC)

# rotate
rows,cols,channel = color_img.shape
M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
color_img = cv2.warpAffine(color_img,M,(cols,rows))

# finish pre processing

gray_img = cv2.cvtColor(color_img,cv2.COLOR_RGB2GRAY)

# gray to binary

retval, binary_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_OTSU)

print(binary_img)

cv2.imshow("Color",color_img)
#cv2.imshow("Gray",gray_img)
cv2.imshow("Binary",binary_img)

inv_binary_img = cv2.bitwise_not(binary_img)

tri_binary = cv2.merge([inv_binary_img, inv_binary_img, inv_binary_img])

#filted_color = color_img.copy()
#for index, i in np.ndenumerate(binary_img):
#	if binary_img[index] == 255:
#		filted_color[index][0] = 0
#		filted_color[index][1] = 0
#		filted_color[index][2] = 0

filted_color = cv2.bitwise_and(color_img,tri_binary)
		
cv2.imshow("FC",filted_color)


(B,G,R) = cv2.split(filted_color)

filted_R_color = filted_color.copy()
for index, i in np.ndenumerate(filted_R_color):
	#print(str(index)+" "+str(i))
	#if i[2]<180:
	#	filted_R_color[index][0]=0
	#	filted_R_color[index][1]=0
	#	filted_R_color[index][2]=0
	if index[2] == 2:
		if i<180:
			filted_R_color[index[0],index[1],0]=0
			filted_R_color[index[0],index[1],1]=0
			filted_R_color[index[0],index[1],2]=0

cv2.imshow("fr",filted_R_color)

# RGB split
#(B,G,R) = cv2.split(color_img)

#cv2.imshow("Red",R)
#cv2.imshow("Green",G)
#cv2.imshow("Blue",B)

#print(B)

#filted_b = binary_img/255*1.0*B
#filted_b = cv2.bitwise_and(B,B,mask=binary_img)

#print(binary_img/255)

#filted_b = B.copy()
#for index, i in np.ndenumerate(binary_img):
#	if binary_img[index] == 255:
#		filted_b[index] = 0

#cv2.imshow("B",B)
#cv2.imshow("FB",filted_b)

# fb to binary

#filted_b_binary_img_r, filted_b_binary_img = cv2.threshold(filted_b, 110, 255, cv2.THRESH_BINARY)

#cv2.imshow("FB",filted_b_binary_img)


#
cv2.waitKey(0)
cv2.destroyAllWindows()