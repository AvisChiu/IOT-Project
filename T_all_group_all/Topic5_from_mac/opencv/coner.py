import cv2
import numpy as np

filename = 'image15.png'

image_width = 1024
image_height = 768


img = cv2.imread(filename)
img = cv2.resize(img, (image_width, image_height), interpolation=cv2.INTER_CUBIC)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
gray = np.float32(gray)
#图像转换为float32
# dst = cv2.cornerHarris(gray,2,3,0.04)
dst = cv2.cornerHarris(gray,5,29,0.04)
#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)#图像膨胀
# Threshold for an optimal value, it may vary depending on the image.
#print(dst)
#img[dst>0.00000001*dst.max()]=[0,0,255] #可以试试这个参数，角点被标记的多余了一些
img[dst>0.01*dst.max()]=[0,0,255]#角点位置用红色标记
#这里的打分值以大于0.01×dst中最大值为边界


cv2.imshow('dst',img)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()

#==========================================================
#==========================================================
#==========================================================

# import numpy as np
# import cv2
# from matplotlib import pyplot as plt 



# image_width = 1024
# image_height = 768

# img = cv2.imread('image15.png')
# img = cv2.resize(img, (image_width, image_height), interpolation=cv2.INTER_CUBIC)
# gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# # corners = cv2.goodFeaturesToTrack(gray,72,0.01,10)#棋盘上的所有点
# corners = cv2.goodFeaturesToTrack(gray,60,0.01,10)

# corners = np.int0(corners)

# for i in corners:
#     x,y = i.ravel()
#     cv2.circle(img,(x,y),2,255,-1)#在原图像上画出角点位置


# cv2.imshow('p',img)
# if cv2.waitKey(0) & 0xff == 27:
#     cv2.destroyAllWindows()


#==========================================================
#==========================================================
#==========================================================


# import numpy as np
# import cv2
# from matplotlib import pyplot as plt

# image_width = 1024
# image_height = 768

# img = cv2.imread('image15.png')
# img = cv2.resize(img, (image_width, image_height), interpolation=cv2.INTER_CUBIC)
# # Initiate FAST object with default values
# fast = cv2.FastFeatureDetector_create()

# # find and draw the keypoints
# kp = fast.detect(img,None)
# img2 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))

# # Print all default params
# print( "Threshold: {}".format(fast.getThreshold()) )
# print( "nonmaxSuppression:{}".format(fast.getNonmaxSuppression()) )
# print( "neighborhood: {}".format(fast.getType()) )
# print( "Total Keypoints with nonmaxSuppression: {}".format(len(kp)) )

# cv2.imshow('fast_true',img2)

# # Disable nonmaxSuppression
# fast.setNonmaxSuppression(0)
# kp = fast.detect(img,None)

# print( "Total Keypoints without nonmaxSuppression: {}".format(len(kp)) )

# img3 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))

# cv2.imshow('fast_false',img3)

# cv2.waitKey()


#==========================================================
#==========================================================
#==========================================================