
"""
Created on Thu Jan  8 10:18:40 2015

@author: bling
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,distance,uniquecolors
from matplotlib import animation
from pandas import Series,DataFrame
MODEL = 'FVCOM'
image_style = 'plot' # or 'animation'
start_time = datetime.now()
stp_num = 4; seg_num = 49
lon_set = [[]]*stp_num; lat_set = [[]]*stp_num
model_points=np.load('model_points.npz')
for i in xrange(stp_num):
    #print len(model_points['lon']),len(model_points['lat'])
    lon_set[i] = model_points['lon'][seg_num*i:seg_num*(1+i)]
    lat_set[i] = model_points['lat'][seg_num*i:seg_num*(1+i)]
arr_lon = np.array(lon_set).T; arr_lat = np.array(lat_set).T
points = {'lats':[],'lons':[]}  # collect all points we've gained
points['lats'].extend(model_points['lat']); points['lons'].extend(model_points['lon'])
#points['lats'].extend(drifter_points['lat']); points['lons'].extend(drifter_points['lon'])
fig = plt.figure() #figsize=(16,9)
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)
plt.title('%d points forecast track %s'%(stp_num,start_time.strftime('%D-%H:%M')))  # %m/%d-%H:%M
colors = uniquecolors(stp_num) #config colors
if image_style=='plot':
    for j in xrange(stp_num):
        ax.annotate('Start %d'%(j+1), xy=(lon_set[j][0],lat_set[j][0]),xytext=(lon_set[j][0]+0.03,lat_set[j][0]+0.03),
                    fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
        ax.plot(lon_set[j],lat_set[j],'o-',color=colors[j],markersize=6,label='Start %d'%(j+1)) #markerfacecolor='r',
if image_style=='animation':
    def animate(n):
        #del ax.lines()
        for j in xrange(stp_num):
            if n==0:
                ax.annotate('Start %d'%(j+1), xy=(lon_set[j][0],lat_set[j][0]),xytext=(lon_set[j][0]+0.03,lat_set[j][0]+0.03),
                            fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
            ax.plot(lon_set[j][:n],lat_set[j][:n],'o-',color=colors[j],markersize=6,label='Start %d'%(j+1)) #markerfacecolor='r',
    anim = animation.FuncAnimation(fig, animate, frames=seg_num, interval=50)
plt.legend(loc='lower right',fontsize=10)
###################################################
en_run_time = datetime.now()
#print 'Take '+str(en_run_time-st_run_time)+' run the code. End at '+str(en_run_time) 
if image_style=='plot':
    plt.savefig('%s-forecast_%s'%(MODEL,en_run_time.strftime("%d-%b-%H:%M")),dpi=400,bbox_inches='tight') #png_dir+
if image_style=='animation':
    anim.save('%s-forecast_%s.gif'%(MODEL,en_run_time.strftime("%d-%b-%H:%M")),writer='imagemagick',fps=5,dpi=150) #ffmpeg,imagemagick,mencoder fps=20'''
plt.show()


