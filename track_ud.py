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
from makegrid import clickmap, points_between, points_square
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,uniquecolors
from matplotlib import animation
st_run_time = datetime.now() # Caculate execution time with en_run_time
############################### Options #######################################
'''
Option 1: We'll get a GIF image includes one drifter track(blue) and two forecast track(red).
          The one of the forecast track starts at first drifter point to contrast with 
          the drifter track; the other one starts at the last drifter point forecasts 
          where it going to.You need to provide Drifter ID, and specify the forecast_days values, 
          which is the forecast days from now.
Option 2: Providing a way specify the start point of the forecast. You can specify point1 
          and point2, or whatever points between the two points. You can also change the forecast_days 
          value, which determines the days of the forecast track of each start points. We will get a
          GIF image ,too.
Option 3: You can add the start points at most nine points on the map provided.You can also change 
          the forecast_days value, which determines the days of the forecast track of each start points. 
          We will get a GIF image ,too.          
'''
######## Hard codes ##########
Option = 1  # 1,2,3
MODEL = 'ROMS'      # 'FVCOM', 'ROMS'
GRID = 'massbay'     # Apply to FVCOM. '30yr', 'massbaya', 'GOM3a', 'GOM3' or 'massbay'
model_days = 1       #MODEL track time(days)
track_way = 'frokward'    # Two option: backward, froward; 'backward' just apply to FVCOM. 
image_style = 'plot'      # Two option: 'plot', animation
#track_time = 0            # Apply to Option 2,3. Starts from now(days) ,positive stands for future,negative stands for past.
start_time = datetime(2015,1,25,16,39,0,0,pytz.UTC)#datetime.now(pytz.UTC)-timedelta(model_days) 
end_time = start_time + timedelta(model_days)
if Option==1:
    drifter_ID = 140420691 #[140410704,140410706,140410707,140410708,140410709] 140430701] 
    INPUT_DATA = 'drift_X.dat'# if raw data, use "drift_X.dat";if want to get drifter data in database, use "None"      
if Option==2: # user specified pts
    point1 = (39.990714, -72.931541)  # Point data structure:(lat,lon)42.0358930225,-70.1035802334,41.912806, -70.152132
    extend_style = 'line' #or 'square'
    if extend_style=='line':
        point2 = ()#41.686903, -70.665452#41.876636, -70.410178
        (st_lat,st_lon)=points_between(point1,point2,1) # The number parameter is the number between the two points.
    if extend_style=='square':  #return a squre points(lats,lons) on center point
        side_length = 0.08
        (st_lat,st_lon) = points_square(point1,side_length)
if Option == 3: # click on a map , press ENTER ended.
    numpts=9 # Points  added on the map at most
    [st_lon,st_lat]=clickmap(numpts) # gets lat/lon by clicking map
        
############################## Extract Data ###################################
loop_length = []
if Option == 1:
    drifter_points = dict(lon=[],lat=[])
    model_points = dict(lon=[],lat=[])
    print "Drifter: %s forecast %d days"%(drifter_ID,model_days)
    #start_time = datetime.now(pytz.UTC)-timedelta(model_days) #datetime(2015,1,24,0,0,0,0,pytz.UTC)
    drifter = get_drifter(drifter_ID, INPUT_DATA)
    dr_points = drifter.get_track(start_time,model_days)
    drifter_points['lon'].extend(dr_points['lon']); drifter_points['lat'].extend(dr_points['lat'])
    #np.savez('drifter_points.npz',lon=drifter_points['lon'],lat=drifter_points['lat'])
    if MODEL=='FVCOM':
        get_obj = get_fvcom(GRID)
        url_fvcom1 = get_obj.get_url(dr_points['time'][0],dr_points['time'][-1])
        point1 = get_obj.get_track(dr_points['lon'][0],dr_points['lat'][0],url_fvcom1,track_way)#,DEPTH        
        end_time2 = dr_points['time'][-1] + timedelta(model_days)
        url_fvcom2 = get_obj.get_url(dr_points['time'][-1],end_time2)
        point2 = get_obj.get_track(dr_points['lon'][-1],dr_points['lat'][-1],url_fvcom2,track_way)#,DEPTH
    if MODEL=='ROMS':
        get_obj = get_roms()
        url_rom1 = get_obj.get_url(dr_points['time'][0],dr_points['time'][-1])
        point1 = get_obj.get_track(dr_points['lon'][0],dr_points['lat'][0],url_rom1,track_way)#,DEPTH
        #end_time2 = dr_points['time'][-1] + timedelta(model_days)
        #url_rom2 = get_obj.get_url(dr_points['time'][-1],end_time2)
        #point2 = get_obj.get_track(dr_points['lon'][-1],dr_points['lat'][-1],url_rom2,track_way)#,DEPTH
    model_points['lon'].extend(point1['lon']); model_points['lat'].extend(point1['lat'])
    #model_points['lon'].extend(point2['lon']); model_points['lat'].extend(point2['lat'])
    loop_length.append(len(drifter_points['lon'])); loop_length.append(len(model_points['lon']))
    #np.savez('model_points.npz',lon=model_points['lon'],lat=model_points['lat'])
if Option==2 or Option==3:
    stp_num = len(st_lat)
    print 'You added %d points.' % stp_num,st_lon,st_lat
    #start_time = datetime.now(pytz.UTC)+timedelta(track_time)  #datetime(2015,2,10,12,0,0,0,pytz.UTC)#
    #end_time = start_time + timedelta(model_days)
    if track_way=='backward':
        end_time = start_time 
        start_time = end_time - timedelta(model_days)  #'''
    lon_set = [[]]*stp_num; lat_set = [[]]*stp_num; 
    for i in range(stp_num):
        if MODEL=='FVCOM': 
            get_obj = get_fvcom(GRID)
            url_fvcom = get_obj.get_url(start_time,end_time)
            point = get_obj.get_track(st_lon[i],st_lat[i],url_fvcom,track_way)
        if MODEL=='ROMS': 
            get_obj = get_roms()
            url_roms = get_obj.get_url(start_time,end_time)
            point = get_obj.get_track(st_lon[i],st_lat[i],url_roms,track_way)
        lon_set[i] = point['lon']; lat_set[i] = point['lat']
        loop_length.append(len(point['lon']))
    #np.savez('model_points.npz',lon=model_points['lon'],lat=model_points['lat'])   
################################## Plot #######################################
points = {'lats':[],'lons':[]}  # collect all points we've gained
#boun_point = np.load('boundary-points.npz')
#lonb = boun_point['lon']; latb = boun_point['lat']
if Option == 1:
    points['lats'].extend(drifter_points['lat']); points['lons'].extend(drifter_points['lon'])
    points['lats'].extend(model_points['lat']); points['lons'].extend(model_points['lon'])
if Option==2 or Option==3:
    for i in range(stp_num):
        points['lons'].extend(lon_set[i])
        points['lats'].extend(lat_set[i])
fig = plt.figure() #figsize=(16,9)
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)  # points is using here
#ax.plot(lonb,latb,'bo',markersize=4)
if Option == 1:
    plt.title('Drifter: {0} {1} forecast'.format(drifter_ID,MODEL))    
    #colors=uniquecolors(len(points['lats'])) #config colors
    an1 = str(dr_points['time'][0].strftime('%m/%d-%H:%M'))
    an2 = str(dr_points['time'][-1].strftime('%m/%d-%H:%M'))
    if image_style=='plot':
        ax.annotate(an1,xy=(dr_points['lon'][0],dr_points['lat'][0]),xytext=(dr_points['lon'][0]+0.03,dr_points['lat'][0]+0.03),
                    fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]''
        ax.annotate(an2,xy=(dr_points['lon'][-1],dr_points['lat'][-1]),xytext=(dr_points['lon'][-1]+0.03,dr_points['lat'][-1]+0.03),
                    fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
        ax.plot(drifter_points['lon'],drifter_points['lat'],'bo-',markersize=6,label='Drifter')
        ax.plot(model_points['lon'],model_points['lat'],'ro',markersize=6,label=MODEL)
    if image_style=='animation':
        def animate(n): # the function of the animation
            if n==0:
                ax.annotate(an1,xy=(dr_points['lon'][0],dr_points['lat'][0]),xytext=(dr_points['lon'][0]+0.03,dr_points['lat'][0]+0.03),
                            fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
            if n==len(drifter_points['lon'])-1:
                ax.annotate(an2,xy=(dr_points['lon'][-1],dr_points['lat'][-1]),xytext=(dr_points['lon'][-1]+0.03,dr_points['lat'][-1]+0.03),
                            fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
            if n<len(drifter_points['lon']):
                ax.plot(drifter_points['lon'][:n+1],drifter_points['lat'][:n+1],'bo-',markersize=6,label='Drifter')
            if n<len(model_points['lon']):
                ax.plot(model_points['lon'][n],model_points['lat'][n],'ro',markersize=6,label=MODEL)
        anim = animation.FuncAnimation(fig, animate, frames=max(loop_length), interval=50)
if Option==2 or Option==3:    
    if track_way=='backward':
        plt.title('%d points %s starting at %s'%(stp_num,track_way,end_time.strftime('%D-%H:%M')))  # %m/%d-%H:%M
    else:
        plt.title('%d points %s starting at %s'%(stp_num,track_way,start_time.strftime('%D-%H:%M')))  # %m/%d-%H:%M
    colors=uniquecolors(stp_num) #config colors
    if image_style=='plot':
        for j in range(stp_num):
            ax.annotate('Start %d'%(j+1), xy=(lon_set[j][0],lat_set[j][0]),xytext=(lon_set[j][0]+0.03,lat_set[j][0]+0.03),
                        fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
            ax.plot(lon_set[j],lat_set[j],'o-',color=colors[j],markersize=6,label='Start %d'%(j+1)) #markerfacecolor='r',
    if image_style=='animation':
        def animate(n):
            #del ax.lines()
            for j in range(stp_num):
                if n==0:
                    ax.annotate('Start %d'%(j+1), xy=(lon_set[j][0],lat_set[j][0]),xytext=(lon_set[j][0]+0.03,lat_set[j][0]+0.03),
                                fontsize=6,arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
                if n<len(lon_set[j]):
                    ax.plot(lon_set[j][:n+1],lat_set[j][:n+1],'o-',color=colors[j],markersize=6,label='Start %d'%(j+1)) #markerfacecolor='r',
        anim = animation.FuncAnimation(fig, animate, frames=max(loop_length), interval=50)
    
###############################################################################
#print max(loop_length)
en_run_time = datetime.now()
print 'Take '+str(en_run_time-st_run_time)+' running the code. End at '+str(en_run_time)
######### Save #########
if image_style=='plot':
    plt.savefig('%s-%s_%s'%(MODEL,track_way,en_run_time.strftime("%d-%b-%H:%M")),dpi=400,bbox_inches='tight') #png_dir+
if image_style=='animation':
    anim.save('%s-%s_%s.gif'%(MODEL,track_way,en_run_time.strftime("%d-%b-%H:%M")),writer='imagemagick',fps=5,dpi=150) #ffmpeg,imagemagick,mencoder fps=20''' 
plt.show()
