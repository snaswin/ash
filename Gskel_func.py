import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage.morphology import convex_hull_image

##################################################################################		
##		Give the Convex-hull image of an input image
##################################################################################		
def hull(img):
	import numpy as np
	from skimage.morphology import convex_hull_image
	
	img=np.array(img)
	imout=convex_hull_image(img)
	return imout

##################################################################################	
##		Give the cross-correlation map of 2 images
##################################################################################	
def cc2d(im1,im2):
	import numpy as np
	from scipy.signal import correlate2d as cc2d
	
	print("The shape of Im1 is ",im1.shape)
	print("The shape of Im2 is ",im2.shape)
	
	out=cc2d(im1,im2)
	return out
	
##################################################################################	
##		Calculate the centroid of input image
##################################################################################		
def MM_cent(im1):
	import numpy as np
	from skimage.measure import moments
	
	I=np.array(im1,dtype=np.double)
	M=moments(I)
	Area=M[0,0]
	cr=M[1,0]/M[0,0]
	cc=M[0,1]/M[0,0]
	centroid=[int(cr),int(cc)]
	
	print("Returning the int-centroid: NOT actual centroid")
	return centroid


##################################################################################	
##		Calculate the area of input image
##################################################################################		
def MM_area(im1):
	import numpy as np
	from skimage.measure import moments
	
	I=np.array(im1,dtype=np.double)
	M=moments(I)
	area=M[0,0]
	return area
	
##################################################################################		
##		This program takes in Gcode img & skel img- gives out the overlap img		
##################################################################################		
def lap_usingCentroid(I1,I2,disp_inputs=False, disp_hulls=False, disp_olay=False):		
	#input should be a binary image
	import numpy as np
	from Gskel_func import cc2d,hull,MM_cent

	I1=(I1).astype(int)
	I2=(I2).astype(int)

	if disp_inputs==True:
		fig=plt.figure()
		splot1=fig.add_subplot(121)
		splot2=fig.add_subplot(122)
		splot1.imshow(I1)
		splot2.imshow(I2)
		plt.show()
		print("Im1",I1.shape)
		print("Im2",I2.shape)

	I1H=hull(I1)
	I2H=hull(I2)

	C1=MM_cent(I1H)
	C2=MM_cent(I2H)
	print("Centroid of I1H is ",C1)
	print("Centroid of I2H is ",C2)

	if disp_hulls==True:					
		fig=plt.figure()
		splot1=fig.add_subplot(121)
		splot2=fig.add_subplot(122)
		splot1.imshow(I1H)
		splot2.imshow(I2H)
		plt.show()

	I1Hpad=np.zeros((2*I1H.shape[0],2*I1H.shape[1]),dtype=int)
	xs=int(I1H.shape[0]/2)
	xe=int((2*I1H.shape[0])-(I1H.shape[0]/2))
	ys=int(I1H.shape[1]/2)
	ye=int((2*I1H.shape[1])-(I1H.shape[1]/2))
	I1Hpad[xs:xe,ys:ye]=I1

	print("Span in Big image: X",xs,xe,"Y",ys,ye)
	
	#plt.imshow(I1Hpad)
	#plt.show()

	C1new=MM_cent(hull(I1Hpad))
	print("Centroid of I1Hpad is ",C1new)
	#Now identifying the start index by fixing centroid of Gcode on that of padding skel Image
	#So, identifying the start position of Gcode image on the big image

	start=[C1new[0]-C2[0],C1new[1]-C2[1]]
	#end will be the resolution of the image
	cent_overlap=I1Hpad
	#This Gain for visual purpose
	#print([start[0],start[0]+I2.shape[0],start[1],start[1]+I2.shape[1]])
	cent_overlap[start[0]:start[0]+I2.shape[0],start[1]:start[1]+I2.shape[1]] = cent_overlap[start[0]:start[0]+I2.shape[0],start[1]:start[1]+I2.shape[1]]+ I2
	
	if disp_olay==True:
		plt.imshow(cent_overlap)
		plt.show()

	return cent_overlap

##################################################################################	
##		Image subtraction
##################################################################################	
def subtract_usingCentroid(I1,I2):		
	#input should be a binary image
	import numpy as np
	from Gskel_func import cc2d,hull,MM_cent

	I1H=(I1).astype(int)
	I2H=(I2).astype(int)
	#no hull being used in this func

	C1=MM_cent(I1H)
	C2=MM_cent(I2H)


	I1Hpad=np.zeros((2*I1H.shape[0],2*I1H.shape[1]),dtype=int)
	
	xs=int(I1H.shape[0]/2)
	xe=int((2*I1H.shape[0])-(I1H.shape[0]/2))
	ys=int(I1H.shape[1]/2)
	ye=int((2*I1H.shape[1])-(I1H.shape[1]/2))
	I1Hpad[xs:xe,ys:ye]=I1

	print("Span in Big image: X",xs,xe,"Y",ys,ye)
	
	#plt.imshow(I1Hpad)
	#plt.show()

	C1new=MM_cent(hull(I1Hpad))
	print("Centroid of I1Hpad is ",C1new)
	#Now identifying the start index by fixing centroid of Gcode on that of padding skel Image
	#So, identifying the start position of Gcode image on the big image

	start=[C1new[0]-C2[0],C1new[1]-C2[1]]
	#end will be the resolution of the image
	cent_overlap=I1Hpad
	#This Gain for visual purpose
	#print([start[0],start[0]+I2.shape[0],start[1],start[1]+I2.shape[1]])
	cent_overlap[start[0]:start[0]+I2.shape[0],start[1]:start[1]+I2.shape[1]] = cent_overlap[start[0]:start[0]+I2.shape[0],start[1]:start[1]+I2.shape[1]]- I2
	
	sub=cent_overlap
	
	return sub




##################################################################################	
##		Rotate an image by an angle wrt center
##################################################################################		

def rotateCent(img,angle,center):
	import numpy as np
	from skimage.transform import rotate
	
	I=np.array(img)
	O=rotate(I,angle,center)
	
	return O
	
##########################################################################
##		Rotational cross correlation between two images	
##########################################################################	
def rotationalCrossCorr(I1,I2,disp=False):
	import numpy as np
	import matplotlib.pyplot as plt
	from skimage.transform import rotate
	from Gskel_func import cc2d,hull,MM_cent, MM_area

	plt.ion()
	I1=np.array(I1)
	I2=np.array(I2)
	I1=I1.astype(int)
	I2=I2.astype(int)

	#I1H=hull(I1)
	#I2H=hull(I2)
	I1H=I1
	I2H=I2

	I1Hpad=np.zeros((2*I1H.shape[0],2*I1H.shape[1]),dtype=int)
	xs=int(I1H.shape[0]/2)
	xe=int((2*I1H.shape[0])-(I1H.shape[0]/2))
	ys=int(I1H.shape[1]/2)
	ye=int((2*I1H.shape[1])-(I1H.shape[1]/2))
	I1Hpad[xs:xe,ys:ye]=I1H

	maxArea=0	
	for angle in range(-35,35):		
		Ibig=I1Hpad
		Ismall=I2H
		OUT=np.zeros((Ibig.shape[0],Ibig.shape[1]),dtype=int)
		C1=MM_cent(Ibig)
		C2=MM_cent(Ismall)
		
		tmp_Ismall=rotate(np.array(Ismall),angle,C2)
		tmp_Ismall=(tmp_Ismall).astype(float)
		#Ismallskel=tmp_Ismall
		#tmp_Ismall=hull(tmp_Ismall)
		
		C1=MM_cent(Ibig)
		C2rot=MM_cent(tmp_Ismall)
		print(C1,C2,C2rot)
		start=[C1[0]-C2rot[0],C1[1]-C2rot[1]]
	
		OUT[start[0]:start[0]+tmp_Ismall.shape[0],start[1]:start[1]+tmp_Ismall.shape[1]] = Ibig[start[0]:start[0]+tmp_Ismall.shape[0],start[1]:start[1]+tmp_Ismall.shape[1]]* tmp_Ismall
		area=MM_area(OUT)
		print("For angle ",angle,",Area of mult is ",area)
		if area>maxArea:
			maxArea=area
			ccAngle=angle
			#rcc=[ccAngle,maxArea]
			rccOUT=np.array([Ibig,Ismall,OUT,maxArea,ccAngle])
		
		if disp==True:
			plt.imshow(tmp_Ismall)
			plt.pause(0.001)
			plt.show()
		plt.pause(0.001)
		
	return rccOUT
