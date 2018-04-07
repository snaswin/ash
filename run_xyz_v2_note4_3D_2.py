import numpy as np
import cv2
import matplotlib.pyplot as plt
	
def gcode2xyz(path,showplot=False,filewrite=False, ):
	import matplotlib.pyplot as plt
	import numpy as np
	import csv
	
	f=open(path,encoding='utf8')
	l1=list(f)

	newl=[]		
	for i in l1:
		tmp=i
		c=tmp[0:2].strip()
		#print(c)
		if c=='G1':
			newl.append(i)
	#newl has all the lines of G-code with G1 command
	################################################
	
	newl2=[]
	for li in newl:		#Here newl has been changed to newl_in after finishing the interpolation code above
		tmp=li[3:]
		newl2.append(tmp)
	#newl2 has (X Y E or X Y F), (Z E or Z F)
	################################################################
	
	#for lin in newl2:
	#	lin=lin.split(' ')
	#	print("length",len(lin),lin)
	
	previousPOS=[-100,-100,-100,-100,False]
	xyze=[]
	for line in newl2:
		tmpline=line
		tmp=tmpline.strip().split(' ')
		
		if len(tmp)==2:
			arg1=tmp[0]
			arg2=tmp[1]
			if arg1[0]=='Z' and arg2[0]=='F':
				Z=float(arg1[1:])	#cal not considered for now
				currentPOS=updateALL(previousPOS,0,0,Z,0,True)
				previousPOS=currentPOS
				xyze.append(currentPOS)
				
			elif arg1[0]=='E' and arg2[0]=='F':
				E=float(arg1[1:])
				currentPOS=updateALL(previousPOS,0,0,0,E,False)
				previousPOS=currentPOS
				xyze.append(currentPOS)
				
		elif len(tmp)==3:
			arg1=tmp[0]
			arg2=tmp[1]
			arg3=tmp[2]
			if arg1[0]=='X' and arg2[0]=='Y' and arg3[0]=='F':
				X=float(arg1[1:])
				Y=float(arg2[1:])
				currentPOS=updateALL(previousPOS,X,Y,0,0,True)
				previousPOS=currentPOS
				xyze.append(currentPOS)
				
			elif arg1[0]=='X' and arg2[0]=='Y' and arg3[0]=='E':
				X=float(arg1[1:])
				Y=float(arg2[1:])
				E=float(arg3[1:])
				currentPOS=updateALL(previousPOS,X,Y,0,E,False)
				previousPOS=currentPOS
				xyze.append(currentPOS)
				
	return xyze
	#xyze is a py LIST of all x,y,z,e in mm.
				
				
	
	
def updateALL(previousPOS,X=0,Y=0,Z=0,E=0,F=False):
	#previousPOS=[x,y,z,e,f]
	currentPOS=[0,0,0,0,False]
	
	if Z!=0 and F!=False:
		currentPOS[0]=previousPOS[0]
		currentPOS[1]=previousPOS[1]
		currentPOS[2]=Z
		currentPOS[3]=previousPOS[3]
		currentPOS[4]=F
				
	elif X!=0 and Y!=0 and E!=0:
		currentPOS[0]=X
		currentPOS[1]=Y
		currentPOS[2]=previousPOS[2]
		currentPOS[3]=E
		currentPOS[4]=F
		
	elif X!=0 and Y!=0 and F!=False:
		currentPOS[0]=X
		currentPOS[1]=Y
		currentPOS[2]=previousPOS[2]
		currentPOS[3]=previousPOS[3]
		currentPOS[4]=F
			
	elif E!=0:
		currentPOS[0]=previousPOS[0]
		currentPOS[1]=previousPOS[1]
		currentPOS[2]=previousPOS[2]
		currentPOS[3]=E
		currentPOS[4]=F
		
	elif X!=0 and Y!=0:
		currentPOS[0]=X
		currentPOS[1]=Y
		currentPOS[2]=previousPOS[2]
		currentPOS[3]=previousPOS[3]
		currentPOS[4]=F
		

	#print(previousPOS," to ",currentPOS)
	#if F is true, it means there was NO extrusion towards that point
	return currentPOS
##################-------------------------------------##################	
def calibrate(xyze,xcal=6.9,ycal=7.1,zcal=10,ecal=1):
	import numpy as np
	xyze=np.array(xyze)
	xyze=xyze.T
	#print(xyze[0])
	
	x=xyze[0]
	y=xyze[1]
	z=xyze[2]
	e=xyze[3]
	f=xyze[4]
	
	X=[]
	for i in x:
		X.append(int(i*xcal))
	#---------------------------------#
	Y=[]
	for j in y:
		Y.append(int(j*ycal))
	#---------------------------------#
	Z=[]
	for k in z:
		Z.append(int(k*zcal))
	#---------------------------------#	
	E=[]
	for l in e:
		E.append(float(l*ecal))
	#---------------------------------#		
	
	xyze_calibrated=[X,Y,Z,E,f]
	
	return xyze_calibrated
	#f is now binary, not boolean


def zfilter(xyze_calibrated):
	
	xyze_calibrated=(np.array(xyze_calibrated)).T
	xyze_zfilt=[]
	for line in range(0,len(xyze_calibrated)-5,5):
		z1=xyze_calibrated[line,2]
		z2=xyze_calibrated[line+1,2]
		z3=xyze_calibrated[line+2,2]
		z4=xyze_calibrated[line+3,2]
		z5=xyze_calibrated[line+4,2]
		ztmp=np.array([z1,z2,z3,z4,z5])
		zBOOL=ztmp>0
		for i in range(len(zBOOL)):
			if zBOOL[i]==False:
				ztmp[i]=0
		zmin=ztmp.min()		
		for i in range(len(ztmp)):		
			if ztmp[i]==zmin:
				xyze_zfilt.append(xyze_calibrated[line+i])
		
	return xyze_zfilt
	
	
def lines(xyze_zfilt,res=[1250,1250,500],thickness=1):
	#Note- here res is the cam resolution.
	#thickness is for the cv2.line
	import numpy as np
	import cv2
	import matplotlib.pyplot as plt
	xyze_zfilt=np.array(xyze_zfilt).tolist()
	
	#Creating a temp image of input resolution
	image=np.zeros((res[0],res[1]),dtype=float)	
	#image3D=np.zeros((roi[0],roi[1],roi[2]),dtype=float)	
	tmp3D=[]
	for i in range(0,len(xyze_zfilt)-1):
		xyimage=np.zeros((res[0],res[1]),dtype=float)	
		line1=xyze_zfilt[i]
		line2=xyze_zfilt[i+1]
		#print("test",line1,"&",line2)
		if line1[2] ==line2[2]:
			if (line1[4]==0 and line2[4]==0) or (line1[4]==1 and line2[4]==0):
				x1=int(line1[0])
				y1=int(line1[1])
				x2=int(line2[0])
				y2=int(line2[1])
				cv2.line(xyimage,(x1,y1),(x2,y2),(127),thickness)		#For ref, cv.Line(img, pt1, pt2, color, thickness=1, lineType=8, shift=0) 
				#thickness is from func arg
				image=image+xyimage
				if line2==xyze_zfilt[-1]:
					tmp3D.append(image)
					image=np.zeros((res[0],res[1]),dtype=float)
					print("Last layer appended")
					
			else:
				print("No interpolation at ",line1,"&",line2)
		elif (line2[2]-line1[2])==1:
			#print("Max/min in image is ",image.max(),image.min())
			#image3D[:,:,int(line1[2]-1)]=image
			tmp3D.append(image)
			image=np.zeros((res[0],res[1]),dtype=float)
			print("Layer appended-",line1[2])
			
		else:
			print("Z did not match at ",line1,"&",line2)
	image3D=np.array(tmp3D) #tmp3D is a list of 2D images
	return image3D	

def normalize_xyze(xyze,tolerance=0.25):
	#tolerance in mm
	import numpy as np
	XYZE=np.array(xyze).T
	X=XYZE[0]
	Y=XYZE[1]
	minx=1000
	miny=1000
	for i in X:
		if i>0:
			if i<minx:
				minx=i
	for i in Y:
		if i>0:
			if i<miny:
				miny=i
	nX=[]
	nY=[]
	for i in X:
		nX.append(i-minx+tolerance)
	for j in Y:
		nY.append(j-miny+tolerance)
			
	print("X and Y are normalized with tolerance ",tolerance,"mm")
	print("Min values used to normalize-",minx,miny)
	
	XYZE[0]=np.array(nX)
	XYZE[1]=np.array(nY)
	
	nor_xyze=XYZE.T
	return nor_xyze

######################################################################
##		Run this to get 3d gcode image
######################################################################
def Gcode(path='threaded_hourglass_NS_5lay.gcode',layer=0):
	#enter layer no to return 2d image
	#OR
	#enter '3d' to return 3d image
	##########################################################
	
	import numpy as np
	import cv2
	import matplotlib.pyplot as plt
	from run_xyz_v2_note4_3D_2 import gcode2xyz,updateALL,calibrate,zfilter,lines,normalize_xyze
		
	xyze=gcode2xyz(path)
	nor_xyze= normalize_xyze(xyze,tolerance=0.25)
	#for l in nor_xyze:
	#	print(l)

	xyze_calibrated=calibrate(nor_xyze,xcal=69,ycal=71,zcal=10,ecal=1)
	xyze_calibrated=np.array(xyze_calibrated)
	zf=np.array(zfilter(xyze_calibrated))
	im3D=lines(zf,thickness=5)

	print("######################")	
	#plt.imsave('imGcode.PNG',im3D[0],origin='lower')
	if layer=='3d':
		return im3D
	elif layer>=0:
		return im3D[layer]
	elif layer=='disp':
		plt.imshow(im3D[0],origin='lower')
		plt.show()
