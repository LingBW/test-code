# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 16:17:19 2014

@author: bling
"""

import sys
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
from matplotlib import path
import calendar
import pytz
import pandas as pd
sys.path.append('../bin')
import netCDF4 
from track_functions import draw_basemap, distance, uniquecolors

DAYS = 4
track_way = 'forwards'
run_time = datetime(2013,6,20,12,0,0,0,pytz.UTC)
points = {'lats':[],'lons':[]}
obj_points = {'lat':[41.801167,41.807005],'lon':[-70.529587,-70.534930]}
points['lats'].extend(obj_points['lat']); points['lons'].extend(obj_points['lon'])
colors=uniquecolors(6) #config colors
fig = plt.figure(figsize=(16,9))
ax1 = fig.add_subplot(231); ax2 = fig.add_subplot(232); ax3 = fig.add_subplot(233)
ax4 = fig.add_subplot(234); ax5 = fig.add_subplot(235); ax6 = fig.add_subplot(236)
loax = [ax1,ax2,ax3,ax4,ax5,ax6]
for j in range(6):
    start_time = run_time + timedelta(j) 
    end_time = start_time + timedelta(DAYS)
    ax = loax[j]
    pts = open('ax%d_points.txt'%(j+1))
    lons = []; lats = []
    for m in pts.readlines():
            s = m.strip()
            k=s.split(',')
            lons.append(float(k[1]))
            lats.append(float(k[0]))
    points['lats'].extend(lats)
    points['lons'].extend(lons)
    v = len(lats)/6
    for i in range(6):     
        stp_ID = 'Start%d' % (i+1)        
        lon = lons[v*i:(v*i+v)]; lat = lats[v*i:(v*i+v)]
        #Calculate the distance separation
        ax.plot(lon,lat, '-',color=colors[i], lw=2, ls='-', marker='o', markersize=2,
                markerfacecolor=colors[i],label=stp_ID)
        ax.annotate(stp_ID, xy=(lon[0],lat[0]),xytext=(lon[0]+0.03,lat[0]+0.01),
                    fontsize=6,arrowprops=dict(arrowstyle="wedge",facecolor=colors[i])) 
                    # connectionstyle="angle3,angleA=0,angleB=-90"
        dist = distance((lat[0],lon[0]),(lat[-1],lon[-1]))    
        print 'The separation to %s is %f kilometers %s.'%(stp_ID,dist[0],track_way)
    ax.plot(obj_points['lon'],obj_points['lat'],'c.',markersize=8)
    ax.text(obj_points['lon'][0],obj_points['lat'][0],'Trash',fontsize=8,rotation=0)
    ax.legend(loc='lower right',fontsize=6)
    '''if j==3 or j==4 or j==5:
        ax.set_xlabel('longitude')
    if j==0 or j==3:
        ax.set_ylabel('latitude')'''
    ax.set_title("%s: %s - %s"%(track_way,start_time.strftime("%m/%d/%Y"),
                                end_time.strftime("%m/%d/%Y")))                            
for ax in loax:
    draw_basemap(fig, ax, points)
fig.subplots_adjust(left=0.15, right=0.9, bottom=0.1, top=0.9)
plt.savefig("%s_%s-days_from_Buzzards_Bay"%(track_way,DAYS,),dpi=400,bbox_inches='tight')
plt.show()