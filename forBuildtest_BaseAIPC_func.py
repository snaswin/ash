#Step 1:
def ash_skel(img):
	import numpy as np
	import matplotlib.pyplot as plt
	import cv2
	from skimage import filters,morphology,util
	from skimage import io
	import skimage
	from mpl_toolkits.mplot3d import axes3d
	from matplotlib import style
	from skimage.filters import threshold_otsu, threshold_local
	from skimage.morphology import skeletonize_3d,skeletonize,thin
	from scipy.ndimage import distance_transform_edt as dist

#	path='im2.JPG'
#	I=cv2.imread(path,0)
	I=np.array(img)
	print("The Img dimensions are",I.shape)
	row=I.shape[0]
	col=I.shape[1]
	II=np.zeros((row,col),dtype=int)
	II=I[230:940,605:1305]
	print("ROI dimensions are ",II.shape)
	J=skimage.exposure.equalize_adapthist(II)
	I=J

	##################################Global 

	global_thresh = threshold_otsu(I)
	I_global = I > global_thresh
	print("Global th completed")

	Iint=I_global.astype(np.uint8)

	###################################Connected Comp labeling
	num, I_labels=cv2.connectedComponents(Iint)
	#Connected component labeling completed
	print(num)
	print(I_labels)
	print("Connected component labeling completed")

	###########################################################
	r=I_labels.shape[0]
	c=I_labels.shape[1]

	print("Separating each label into separate planes...")
	I_labSep=np.zeros((r,c,num),dtype=int)
	#Separating labels to calculate area
	for n in range(num):
		for i in range(r):
			for j in range(c):
				if I_labels[i,j]==n:
					I_labSep[i,j,n]=1
					

	area=[]
	print("Finding the area of each blob in those planes...")
	for n in range(I_labSep.shape[2]):
		c=0
		for i in range(I_labSep.shape[0]):
			for j in range(I_labSep.shape[1]):
				if I_labSep[i,j,n]>0:
					c=c+1
		area.append(c)
	print("Area of all labels are ",area)	


	blobth=20 	#Threshold to blob size
	small_blob_ind=[]	#List of Index for small blobs
	for a in range(len(area)):
		if area[a]<blobth:				#Less than th bcoz we extracting small blobs
			small_blob_ind.append(a)
	print("List of small blobs are ",small_blob_ind)

	#Removing all small blobs - less than blobth

	tmp=I_labels
	for s in small_blob_ind:
		for i in range(tmp.shape[0]):
			for j in range(tmp.shape[1]):
				if tmp[i,j]==s:
					tmp[i,j]=0

	print("Bye bye Small blobs")

	print("Here's are the Big blobs")

	###########################################################

	layer=np.zeros((tmp.shape[0],tmp.shape[1]),dtype=int)
	for i in range(layer.shape[0]):
		for j in range(layer.shape[1]):
			if tmp[i,j]>0:
				layer[i,j]=1

	layer=np.array(layer,dtype=int)
	###########################################################
	#s3=skeletonize_3d(layer)
	###########################################################
	D=dist(layer)	
	###########################################################
	
	return layer,D

#Step2
def runfullbuild(I):
	from forBuildtest_BaseAIPC_func import ash_skel
	import numpy as np
	import matplotlib.pyplot as plt
	import cv2
	from skimage import filters,morphology,util
	from skimage import io
	import skimage
	from mpl_toolkits.mplot3d import axes3d
	from matplotlib import style
	from skimage.filters import threshold_otsu, threshold_local
	from skimage.morphology import skeletonize_3d,skeletonize,thin
	from scipy.ndimage import distance_transform_edt as dist
	import glob
	#from packrun500 import packrun_sk500
	from mpl_toolkits.mplot3d import axes3d
	from scipy.signal import medfilt2d
	from skimage.color import rgb2gray
	from timeit import default_timer as timer

	#Starting Timer
	start=timer()
	#########################Algo is here! ##################################
	#Step1
	layer,D=ash_skel(I)
	#Step2
	Dnew=DnewMed=Ds3=Ioverlay=O_skel_lay=O_skel_orig=np.zeros((layer.shape[0],layer.shape[1]),dtype=np.uint16)
	
	Dmx=D.max()
	Dth=Dmx/5
	Dnew=D>Dth
	#Step3
	DnewMed=medfilt2d(np.array((Dnew),dtype=np.uint8) )
	#Step4
	Ds3=skeletonize_3d(DnewMed)
	
	##########################
	Ds3_thick=np.zeros((D.shape[0],D.shape[1]),dtype=int)
	for i in range(Ds3.shape[0]):
		for j in range(Ds3.shape[1]):
			if Ds3[i,j]>0:
				#s3D[i,j]=(s3[i,j]/255)*D[i,j]
				Ds3_thick[i,j]=D[i,j]
	#Ds3_thick is the thickness of path at each point in skeleton3d
	Thick=2*Ds3_thick
	#Thickness at each point is Thick
	
	
	#Step5:- Overlay of skel on layer
	Os_lay=layer+(3*(Ds3))
	#Step6:- Overlay of skel on Image		#ROI is I[230:940,605:1305]
	roi=rgb2gray(I[230:940,605:1305])
	Os_orig=roi+Ds3*100
	
	########################################################################
	#Ending timer
	duration=timer()-start
	print("The Duration of the program for this image is ",duration)
	#Return variables are ROI,Ds3,Os_lay,Os_orig
	
	
	return roi,Ds3,Thick,Os_lay,Os_orig
