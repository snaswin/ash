#Run Gskel_func

import numpy as np
import cv2
import matplotlib.pyplot as plt
import Gskel_func
from Gskel_func import lap_usingCentroid,rotateCent,MM_cent,rotationalCrossCorr

I1=plt.imread('im1skel.PNG')
I2=plt.imread('gcode.PNG')

I1=np.array(I1)
I2=np.array(I2)

I1=I1[:,:,0]
I2=I2[:,:,0]

I1=(I1>0.5).astype(int)
I2=(I2<0.25).astype(int)

#olap=lap_usingCentroid(I1,I2)
center=tuple(MM_cent(I1))
#olap=rotateCent(I1,-45,center)

rccout=rotationalCrossCorr(I1,I2,disp=True)
big=rccout[0]
small=rccout[1]
bigsmall=rccout[2]
rccarea=rccout[3]
rccangle=rccout[4]

plt.imshow(bigsmall)
plt.show()
print("Cross Correlation angle ",rccangle,rccarea)

plt.imshow(small)
plt.show()
