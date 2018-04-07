import numpy as np
from forBuildtest_BaseAIPC_func import runfullbuild
from run_xyz_v2_note4_3D_2 import Gcode
from Gskel_func import lap_usingCentroid, subtract_usingCentroid
from skimage.transform import rotate
import cv2
import matplotlib.pyplot as plt


Icam=plt.imread('full.jpg')
Icam=Icam[:,:,0]
Iflip=Icam[::-1,::-1]
####------------------########
##  	skel extraction	######
####------------------########

roi,Ds3,Thick,lay,orig=runfullbuild(Iflip)
####------------------########
##		Gcode image
####------------------########

g0=Gcode(layer=0)
gr0=rotate(g0,angle=-90)

#plt.imshow(g0)
#plt.show()

Gsk=lap_usingCentroid(255*Ds3,gr0)

plt.imshow(Gsk)
plt.show()

####------------------########
##		Error points
####------------------########

sub=subtract_usingCentroid(Ds3,gr0)
sub=sub>0

plt.imshow(sub)
plt.show()

