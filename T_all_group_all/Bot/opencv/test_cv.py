import numpy as np
import cv2

#image_file = 'image1.png'
image_file = 'img0.png'
#image_file = 'image11.png'
#image_file = 'image12.png'
#image_file = 'image13.png'

#cv2.IMREAD_COLOR
#IMREAD_GRAYSCALE

image_width = 1024
image_height = 768

img = cv2.imread(image_file,cv2.IMREAD_COLOR)
# resize
img = cv2.resize(img, (image_width, image_height), interpolation=cv2.INTER_CUBIC)
# rotate

rows,cols,channel = img.shape

M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
img = cv2.warpAffine(img,M,(cols,rows))

# filter

(B,G,R) = cv2.split(img)

cv2.imshow("Red",R)
cv2.imshow("Green",G)
cv2.imshow("Blue",B)

grey = R

# binary
retval, dst = cv2.threshold(grey, 0, 255, cv2.THRESH_OTSU)

color = dst[1:50,10:500]

cv2.imshow('color',color)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

try:
	black_count = np.sum(color == 0)
	black_index = np.where(color == 0)
	#if black_count == 0:
	#	black_count = 1
	print(black_index)
	
	#center = (black_index[0][black_count - 1] + black_index[0][0]) / 2
	center = np.sum(black_index)/black_count
	print(center)
	#print(center)
	direction = center - image_width/2
	print(direction)
	
	turn = (image_width/2 - center)/image_width
	
	print(turn)
	
except Exception as e:
	print(e)

print(dst.shape)

cv2.imshow('image',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()