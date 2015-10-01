# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 14:12:44 2015

@author: bling
"""

from sympy import *
from sympy.geometry import *
import math
import matplotlib.pyplot as plt
from fractions import Fraction

def rotate_vector(v, angle):
    """Rotate a vector `v` by the given angle(radian)."""
    x, y = v

    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    nx = x*cos_theta - y*sin_theta
    ny = x*sin_theta + y*cos_theta

    return [nx, ny]

def uvreflection1(f1,f2,b1,b2,v):
    '''
    Return reflection point.
    f2 is a forcast point from f1. 
    b1,b2 are boundary point.
    Format (lon,lat)
    '''
    fl = Line(f1,f2)
    bl = Line(b1,b2)
    anchor = intersection(fl,bl)[0]
    
    anchor = str(anchor)[6:-1]
    anchor = anchor.split(','); print 'anchor:', anchor
    interpx = Fraction(anchor[0]); interpy = Fraction(anchor[1])    
    anchor = [float(interpx),float(interpy)]
    #angle : angle in radians'''
    #ag1 = Line(anchor,b1); ag2 = Line(anchor,b2); ab = Line(anchor,f1)
    #af1 = ab.angle_between(ag1)
    angle = fl.angle_between(bl); print angle
    if angle > pi/2:
        angle1 = pi-angle
    #angle = 360-angle*180/pi
    else:
        angle1 = angle#'''
    angle2 = 2*angle1
    v1 = rotate_vector(v, angle2); #print 'reflection:', v1
    fp = ((anchor[0]+v1[0]), (anchor[1]+v1[1])) #reflection point
    tg = Line(anchor,fp)
    tg1 = Line(anchor,b1)
    tg2 = Line(anchor,b2)
    tag1 = tg1.angle_between(tg); #print tag1
    tag2 = tg2.angle_between(tg); #print tag2
    #fl2 = Segment(f1,fp)
    #print intersection(fl2,bl)
    if tag1 == angle or tag2 == angle:
        #print 'angle1:', angle
        fp = (round(fp[0],6),round(fp[1],6))
        return fp, anchor
    else:
        angle2 = 2*pi-angle2 ; #print 'angle2:'
        v1 = rotate_vector(v, angle2)
        fp = (round((anchor[0]+v1[0]),6), round((anchor[1]+v1[1]),6))
        return fp, anchor
        
v = (8,18)
#anchor=(0,0)
#angle=pi/6  
f1 = (1,1)
f2 = (v[0]+f1[0],v[1]+f1[1])
b2 = (0,6)
b1 = (6,0)

p2, interp = uvreflection1(f1,f2,b1,b2,v)
#v2 = rotate_vector(v, angle)
print p2
#plt.scatter(f1[0],f1[1])
# boundary line: black
plt.plot([b1[0],b2[0]],[b1[1],b2[1]],'ko-')
# shoot line: blue
plt.plot([f1[0],interp[0]],[f1[1],interp[1]],'bo-')
# reflection line: red
plt.plot([interp[0],p2[0]],[interp[1],p2[1]],'ro-')
plt.axis('equal')
plt.show()
