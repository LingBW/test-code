# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 22:04:37 2014

@author: handry
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 15:54:43 2014

@author: bling
"""

import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,distance,uniquecolors
from matplotlib import animation

st_run_time = datetime.now()
DAYS = 3                     # Length of time wanted in track
MODEL = 'FVCOM'              # 'FVCOM', 'ROMS' or 'BOTH'
DEPTH = -1.                  # depth of drogue in meters

MODE = 'FORCAST'           # 'FORECAST' or 'HINDCAST'
GRID = 'massbay'            # '30yr', 'massbaya', 'GOM3a', 'GOM3' or 'massbay'
# if raw data, use "drift_X.dat";if want to get drifter data in database, use "None"
INPUT_DATA = 'drift_X.dat'   
run_time = datetime(2015,1,24,0,0,0,0,pytz.UTC)

drifter_ids = [140410704,140410706,140410707,140410708,140410709] #[140410701]
drifter_ID = 140430701
##########################################
points = {'lats':[],'lons':[]}
dr_set={'lats':[],'lons':[]}
fc_set={'lats':[],'lons':[]}
d_file = open('dr_points.txt')
f_file = open('fc_points.txt')
###
for m in d_file.readlines():
        s = m.strip()
        k=s.split(',')
        dr_set['lons'].append(float(k[1]))
        dr_set['lats'].append(float(k[0]))
points['lats'].extend(dr_set['lats'])
points['lons'].extend(dr_set['lons'])
for m in f_file.readlines():
        s = m.strip()
        k=s.split(',')
        fc_set['lons'].append(float(k[1]))
        fc_set['lats'].append(float(k[0]))
points['lats'].extend(fc_set['lats'])
points['lons'].extend(fc_set['lons'])
##############################################
fig = plt.figure()
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)
'''ax.plot(dr_set['lons'][0],dr_set['lats'][0],'c.',markersize=16) #,label='Startpoint'
ax.annotate('24/1', xy=(dr_set['lons'][0]+0.005,dr_set['lats'][0]+0.005),fontsize=6,
            xytext=(dr_set['lons'][0]+0.03,dr_set['lats'][0]+0.03),
            arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]'''
#colors=uniquecolors(len(points['lats'])) #config colors
plt.title('Drifter {0}: {1} track'.format(drifter_ID,MODE))
########################
a0 = 12; a1 = 23; a2 = 34
def animate(n):
    #ax.cla()
    #del ax.lines() #apply to plot
    #del ax.collection() #apply to scatter  

    #d_lon = dr_set['lons'][:n]; d_lat = dr_set['lats'][:n]
    #f_lon = fc_set['lons'][:n]; f_lat = fc_set['lats'][:n]
    if n<a0:
        if n==0:
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            ax.annotate('24/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
            pass
        ax.plot(dr_set['lons'][n-1:n+1],dr_set['lats'][n-1:n+1],'bo-',markersize=6,label='Drifter')#10-n%5
        ax.plot(fc_set['lons'][:n],fc_set['lats'][:n],'go-',markersize=4,label='%s'%MODE)
    if n>=a0 and n<a1:
        if n==a0:
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            ax.annotate('25/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        ax.plot(dr_set['lons'][n-1:n+1],dr_set['lats'][n-1:n+1],'bo-',markersize=6,label='Drifter')
        ax.plot(fc_set['lons'][a0:n],fc_set['lats'][a0:n],'yo-',markersize=4,label='%s'%MODE)
    if n>=a1 and n<a2:
        if n==a1:
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            ax.annotate('26/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        if n==(a2-1):
            ax.plot(dr_set['lons'][n-1:-1],dr_set['lats'][n-1:-1],'bo-',markersize=6,label='Drifter')
            pass
        ax.plot(dr_set['lons'][n-1:n+1],dr_set['lats'][n-1:n+1],'bo-',markersize=6,label='Drifter')
        ax.plot(fc_set['lons'][a1:n],fc_set['lats'][a1:n],'co-',markersize=4,label='%s'%MODE)
        
    if n>=a2:
        if n==a2:
            po = (fc_set['lons'][n]+0.005,fc_set['lats'][n]+0.005)
            pt = (fc_set['lons'][n]+0.03,fc_set['lats'][n]+0.03)
            ax.annotate('26/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        ax.plot(fc_set['lons'][a2:n],fc_set['lats'][a2:n],'ro-',markersize=4,label='%s'%MODE)
    ''''del ax.lines[:]
    if n<5:
        ax.plot(fc_set['lons'][:n],fc_set['lats'][:n],'ro',markersize=(10-n%5),label='%s'%MODE) 
        #,markerfacecolor='r''%d'%n ,color='r' ,linewidth=4 ,marker='o'
        if n<len(dr_set['lons']):
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            if n==12:
                ax.annotate('25/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
            if n==23:
                ax.annotate('26/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
            if n==29:
                ax.annotate('26/1 12:00',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
            ax.plot(dr_set['lons'][:n],dr_set['lats'][:n],'bo-',markersize=(10-n%5),label='Drifter')
    if n>=5:
        ax.plot(fc_set['lons'][n-5:n],fc_set['lats'][n-5:n],'ro',markersize=(10-n%5),label='%s'%MODE) 
        #,markerfacecolor='r''%d'%n ,color='r' ,linewidth=4 ,marker='o'
        if n<len(dr_set['lons']):
            po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
            pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
            if n==12:
                ax.annotate('25/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
            if n==23:
                ax.annotate('26/1',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
            if n==31:
                ax.annotate('26/1 14:31',xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
            ax.plot(dr_set['lons'][n-5:n],dr_set['lats'][n-5:n],'bo-',markersize=(10-n%5),label='Drifter')
    '''
anim = animation.FuncAnimation(fig, animate, frames=len(fc_set['lons']), interval=50)
plt.legend(loc='lower right',fontsize=10)
en_run_time = datetime.now()
print 'Take '+str(en_run_time-st_run_time)+' run the code. End at '+str(en_run_time)
#anim.save('%s multi-days_demo.gif'%drifter_ID, writer='imagemagick',fps=10,dpi=100) #ffmpeg,imagemagick,mencoder fps=20
anim.save('%s-demo_%s.gif'%(drifter_ID,en_run_time.strftime("%d-DEC-%H:%M")),
          writer='imagemagick',fps=5,dpi=150) #ffmpeg,imagemagick,mencoder fps=20
plt.show()

