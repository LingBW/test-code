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
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,distance,uniquecolors
from matplotlib import animation
st_run_time = datetime.now() # Caculate the time running the code with en_run_time 
######################### Option ##############################
drifter_ID = 140420691 #[140410704,140410706,140410707,140410708,140410709] 140430701]
# if raw data, use "drift_X.dat";if want to get drifter data in database, use "None"
INPUT_DATA = 'drift_X.dat' 
MODEL = 'ROMS'              # 'FVCOM', 'ROMS' or 'BOTH'                  
GRID = 'massbay'            # '30yr', 'massbaya', 'GOM3a', 'GOM3' or 'massbay' (needed foe FVCOM model only)
MODE = 'FORECAST'           # 'FORECAST' or 'HINDCAST'
DEPTH = -1.               # depth of drogue in meters
DAYS = 3                     # Length of time wanted in track
run_time = datetime(2015,1,24,0,0,0,0,pytz.UTC)
print "Drifter: %s track %d days"%(drifter_ID,DAYS)
########################## Extract points ##################################
dr_set={'lats':[],'lons':[]}  # initialize all points of Drifter
fc_set={'lats':[],'lons':[]}  # initialize points of MODEL
d_file = open('dr_points.txt','w') # opens an output file for portion of drifters simulated
f_file = open('fc_points.txt','w') # opens an output file for modeled track
a0=int();a1=int();a2=int()  # use to record position of the labeled points on the track
an0=str();an1=str();an2=str()  # record the start time of the labeled points
a = [a0,a1,a2]; an = [an0,an1,an2]
for i in range(DAYS):    
    begin_time = run_time + timedelta(i)  # add one day with each time through the for-loop
    print '%dth day.'%(i+1)  #,begin_time.strftime('%m/%d/%Y %H:%M'))
    drifter = get_drifter(drifter_ID, INPUT_DATA)
    dr_points = drifter.get_track(begin_time,1) # gets drifter track beginning at begin_time
    dr_set['lons'].extend(dr_points['lon']); dr_set['lats'].extend(dr_points['lat'])
    for h in zip(dr_points['lat'],dr_points['lon']): d_file.write('%f,%f\n'%h) #saves drifter specified data to file
    st_point = (dr_points['lon'][0],dr_points['lat'][0]) # to be used later to start the model
    start_time = dr_points['time'][0]  # start time of the MODEL
    end_time = start_time + timedelta(1) # assumes you are only stepping through one day
    a[i] = len(dr_set['lats']); an[i] = start_time.strftime('%m/%d-%H:%M') # 
    print 'Drifter points',a[i],an[i]
    if MODEL in ('FVCOM','BOTH'):
        get_obj = get_fvcom(GRID)
        url_fvcom = get_obj.get_url(start_time,end_time)
        point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_fvcom) # where "point" output is a dictionary result
    if MODEL in ('ROMS', 'BOTH'):
        get_obj = get_roms()
        url_roms = get_obj.get_url(start_time, end_time)
        point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_roms) #includes start point
    #print len(point['lon'])
    n = len(dr_points['lat'])  # Quantity of one-day's drifter points
    #save the the same quantity of drifter
    fc_set['lons'].extend(point['lon'][:n]); fc_set['lats'].extend(point['lat'][:n])
    for h in zip(point['lat'][:n],point['lon'][:n]): f_file.write('%f,%f\n'%h)
d_file.close()
'''forecast two days after the last drifter point.'''
start_time = dr_points['time'][-1]
print 'Beginning of 2-days forcast.',start_time 
end_time = start_time + timedelta(2) # assumes 2-day forecast
an3 = start_time.strftime('%m/%d-%H:%M') # %H:%M
st_point = (dr_set['lons'][-1],dr_set['lats'][-1])  # Position of the last drifter point
if MODEL in ('FVCOM','BOTH'):
    get_obj = get_fvcom(GRID)
    url_fvcom = get_obj.get_url(start_time,end_time)
    point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_fvcom)
if MODEL in ('ROMS', 'BOTH'):
    get_obj = get_roms()
    url_roms = get_obj.get_url(start_time, end_time)
    point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_roms)
fc_set['lons'].extend(point['lon']); fc_set['lats'].extend(point['lat']) 
for h in zip(point['lat'],point['lon']): f_file.write('%f,%f\n'%h)
f_file.close()
#################### Plotting ##########################
points = {'lats':[],'lons':[]}  # collect all points we've gained
points['lats'].extend(dr_set['lats']); points['lons'].extend(dr_set['lons'])
points['lats'].extend(fc_set['lats']); points['lons'].extend(fc_set['lons'])
fig = plt.figure() #figsize=(16,9)
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)
'''ax.plot(dr_set['lons'][0],dr_set['lats'][0],'c.',markersize=16) #,label='Startpoint'
ax.annotate(an[0], xy=(dr_set['lons'][0]+0.005,dr_set['lats'][0]+0.005),fontsize=6,
            xytext=(dr_set['lons'][0]+0.03,dr_set['lats'][0]+0.03),
            arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
#colors=uniquecolors(len(points['lats'])) #config colors
plt.title('Drifter: {0} {1} track'.format(drifter_ID,MODE))
################
def animate(n):  # the function of the animation
    #ax.cla()
    #del ax.lines() #apply to plot
    #del ax.collection() #apply to scatter
    if n<a[0]:
        if n==0:
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            ax.annotate(an[0],xy=po,xytext=pt,fontsize=8,arrowprops=dict(arrowstyle="wedge"))
            pass
        ax.plot(dr_set['lons'][n-1:n+1],dr_set['lats'][n-1:n+1],'bo-',markersize=6,label='Drifter')#10-n%5
        ax.plot(fc_set['lons'][:n],fc_set['lats'][:n],'go-',markersize=4,label='%s'%MODE)
    if n>=a[0] and n<a[1]:
        if n==a[0]:
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            ax.annotate(an[1],xy=po,xytext=pt,fontsize=8,arrowprops=dict(arrowstyle="wedge"))
        ax.plot(dr_set['lons'][n-1:n+1],dr_set['lats'][n-1:n+1],'bo-',markersize=6,label='Drifter')
        ax.plot(fc_set['lons'][a[0]:n],fc_set['lats'][a[0]:n],'yo-',markersize=4,label='%s'%MODE)
    if n>=a[1] and n<a[2]:
        if n==a[1]:
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            ax.annotate(an[2],xy=po,xytext=pt,fontsize=8,arrowprops=dict(arrowstyle="wedge"))
        if n==(a[2]-1):
            ax.plot(dr_set['lons'][n-1:-1],dr_set['lats'][n-1:-1],'bo-',markersize=6,label='Drifter')
            pass
        ax.plot(dr_set['lons'][n-1:n+1],dr_set['lats'][n-1:n+1],'bo-',markersize=6,label='Drifter')
        ax.plot(fc_set['lons'][a[1]:n],fc_set['lats'][a[1]:n],'co-',markersize=4,label='%s'%MODE)        
    if n>=a[2]:
        if n==a[2]:
            po = (fc_set['lons'][n]+0.005,fc_set['lats'][n]+0.005)
            pt = (fc_set['lons'][n]+0.03,fc_set['lats'][n]+0.03)
            ax.annotate(an3,xy=po,xytext=pt,fontsize=8,arrowprops=dict(arrowstyle="wedge"))
        ax.plot(fc_set['lons'][a[2]:n],fc_set['lats'][a[2]:n],'ro-',markersize=4,label='%s'%MODE)
    '''ax.plot(fc_set['lons'][n],fc_set['lats'][n],'ro',markersize=4,label='%s'%MODE) #'%d'%n 
    if n<len(dr_set['lons']):
        po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
        pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
        if n==a[0]:
            ax.annotate(an[1],xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        if n==a[1]:
            ax.annotate(an[2],xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        if n==(a[2]-1):
            ax.annotate(an3,xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        ax.plot(dr_set['lons'][n],dr_set['lats'][n],'bo-',markersize=6,label='drifter')'''   
anim = animation.FuncAnimation(fig, animate, frames=len(fc_set['lons']), interval=50)
plt.legend(loc='lower right',fontsize=10)
###################################################
en_run_time = datetime.now()
print 'Take '+str(en_run_time-st_run_time)+' run the code. End at '+str(en_run_time)
#anim.save('%s multi-days_demo.mp4'%drifter_ID, writer='mencoder',fps=10,dpi=200) 
anim.save('%s-demo_%s.gif'%(drifter_ID,en_run_time.strftime("%d-DEC-%H:%M")),
          writer='imagemagick',fps=5,dpi=150) #ffmpeg,imagemagick,mencoder fps=20
plt.show()
