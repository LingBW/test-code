# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 15:54:43 2014
Derived from previous particle tracking work by Manning, Muse, Cui, Warren.
This now generates an animation if requested.
This project plots both the drifter track and forcast track for the last three days and forecasts 
the drifter track for the next two days. 
@author: bling
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from makegrid import clickmap, points_between
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,distance,uniquecolors
from matplotlib import animation
st_run_time = datetime.now() # Caculate the time running the code with en_run_time

def extract_fvcom_point(sart_time, end_time, st_lon, st_lat):       
    DEPTH = -1
    GRID = 'massbay'     # '30yr', 'massbaya', 'GOM3a', 'GOM3' or 'massbay'
    get_obj = get_fvcom(GRID)
    url_fvcom = get_obj.get_url(start_time,end_time)
    point = get_obj.get_track(st_lon,st_lat,DEPTH,url_fvcom)
    return point
def extract_roms_point(sart_time, end_time, st_lon, st_lat):
    DEPTH = -1
    get_obj = get_roms()
    url_roms = get_obj.get_url(start_time,end_time)
    point = get_obj.get_track(st_lon,st_lat,DEPTH,url_roms)
    return point
############################### Options #######################################
'''
Option 1: ...
Option 2: ....
Option 3: ....
'''
Option = 3  # 2,3
#################
if Option == 1:    
    drifter_ID = 140420691 #[140410704,140410706,140410707,140410708,140410709] 140430701] 
    start_time = datetime(2015,1,24,0,0,0,0,pytz.UTC)           
    forecast_days = 2
    MODEL = 'FVCOM'              # 'FVCOM', 'ROMS' or 'BOTH'                     
    #MODE = 'FORECAST'           # 'FORECAST' or 'HINDCAST'
    INPUT_DATA = 'drift_X.dat'# if raw data, use "drift_X.dat";if want to get drifter data in database, use "None"    
    print "Drifter: %s forecast %d days"%(drifter_ID,forecast_days)
elif Option==2: # user specified pts    
    start_time = datetime(2015,1,28,0,0,0,0,pytz.UTC)
    forecast_days = 1
    MODEL = 'FVCOM'
    #track_way = 'forwards' # two options: forwards,backwards   
    point1 = (42.013508, -70.289329)  # Point data structure:(lat,lon)
    point2 = ()#41.686903, -70.665452#41.876636, -70.410178
    (st_lat,st_lon)=points_between(point1,point2,1)
    print st_lat,st_lon
    stp_num = len(st_lat)
    print 'You added %d points.' % stp_num
elif Option == 3: # click on a map    
    start_time = datetime(2015,1,28,0,0,0,0,pytz.UTC)
    forecast_days = 1
    MODEL = 'FVCOM'
    #track_way = 'forwards' # two options: forwards,backwards
    numpts=9 # at most added on the map
    [st_lon,st_lat]=clickmap(numpts) # gets lat/lon by clicking map
    print st_lat,st_lon
    stp_num = len(st_lat)
    print 'You added %d points.' % stp_num
############################## Extract Data ###################################
drifter_points = dict(lon=[],lat=[])
model_points = dict(lon=[],lat=[])
if Option == 1:
    drifter = get_drifter(drifter_ID, INPUT_DATA)
    dr_points = drifter.get_track(start_time,)
    drifter_points['lon'].extend(dr_points['lon']); drifter_points['lat'].extend(dr_points['lat'])
    if MODEL=='FVCOM':
        point1 = extract_fvcom_point(dr_points['time'][0],dr_points['time'][-1],dr_points['lon'][0],dr_points['lat'][0])
        end_time2 = dr_points['time'][-1] + timedelta(forecast_days)
        point2 = extract_fvcom_point(dr_points['time'][-1],end_time2,dr_points['lon'][-1],dr_points['lat'][-1])
    if MODEL=='ROMS':
        point1 = extract_roms_point(dr_points['time'][0],dr_points['time'][-1],dr_points['lon'][0],dr_points['lat'][0])
        end_time2 = dr_points['time'][-1] + timedelta(forecast_days)
        point2 = extract_roms_point(dr_points['time'][-1],end_time2,dr_points['lon'][-1],dr_points['lat'][-1])
    model_points['lon'].extend(point1['lon']); model_points['lat'].extend(point1['lat'])
    model_points['lon'].extend(point2['lon']); model_points['lat'].extend(point2['lat'])
if Option==2 or Option==3:   
    end_time = start_time + timedelta(forecast_days)
    for i in range(len(st_lat)):
        if MODEL=='FVCOM': point = extract_fvcom_point(start_time,end_time,st_lon[i],st_lat[i])        
        if MODEL=='ROMS': point = extract_roms_point(start_time,end_time,st_lon[i],st_lat[i])
        model_points['lon'].extend(point['lon']); model_points['lat'].extend(point['lat'])
    np.savez('model_points.npz',lon=model_points['lon'],lat=model_points['lat'])
    lon_set = [[]]*stp_num; lat_set = [[]]*stp_num
    seg_num = len(model_points['lon'])/stp_num
    for i in xrange(stp_num):
        lon_set[i] = model_points['lon'][seg_num*i:seg_num*(1+i)]
        lat_set[i] = model_points['lat'][seg_num*i:seg_num*(1+i)]
    arr_lon = np.array(lon_set).T; arr_lat = np.array(lat_set).T
    
################################## Plot #######################################
points = {'lats':[],'lons':[]}  # collect all points we've gained
points['lats'].extend(model_points['lat']); points['lons'].extend(model_points['lon'])
points['lats'].extend(drifter_points['lat']); points['lons'].extend(drifter_points['lon'])
fig = plt.figure() #figsize=(16,9)
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)
if Option == 1:
    plt.title('Drifter: {0} {1} track'.format(drifter_ID,MODEL))
    #colors=uniquecolors(len(points['lats'])) #config colors
if Option==2 or Option==3:    
    plt.title('forecast track')#('Drifter: {0} {1} track'.format(drifter_ID,MODE))
    #colors=uniquecolors(len(points['lats'])) #config colors
    def animate(n): # the function of the animation
        #ax.cla()#del ax.lines() #apply to plot#del ax.collection() #apply to scatter
        ax.plot(arr_lon[n],arr_lat[n],'ro',markersize=8,label='forecast')
    anim = animation.FuncAnimation(fig, animate, frames=seg_num, interval=50)
    en_run_time = datetime.now()
    anim.save('%s-demo_%s.gif'%(MODEL,en_run_time.strftime("%d-DEC-%H:%M")),
          writer='imagemagick',fps=5,dpi=150) #ffmpeg,imagemagick,mencoder fps=20'''
###################################################
print 'Take '+str(en_run_time-st_run_time)+' running the code. End at '+str(en_run_time) 
plt.show()
