# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 11:37:32 2015

@author: bling
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from makegrid import clickmap, points_between, points_square
from track_functions import extract_drifter_point,extract_fvcom_point,extract_roms_point,draw_basemap,uniquecolors,get_fvcom
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
Option = 2  # 1,2,3
MODEL = 'FVCOM'              # 'FVCOM', 'ROMS'
GRID = 'massbay'     # '30yr', 'massbaya', 'GOM3a', 'GOM3' or 'massbay'
forecast_days = 1
track_time = 0 # Apply to Option2,3. Starts from now ,positive stands for future,negative stands for past.
track_way = 'backward'  # Two option: backward, forward
image_style = 'animation' # Two option: 'plot', animation
     
start_time = datetime.now(pytz.UTC)+timedelta(track_time)  #datetime(2015,2,10,12,0,0,0,pytz.UTC)#
end_time = start_time + timedelta(forecast_days)
point1 = (41.912806, -70.152132)  # Point data structure:(lat,lon)42.0358930225,-70.1035802334,41.912806, -70.152132
    

drifter_points = dict(lon=[],lat=[])
points = dict(lons=[],lats=[])
DEPTH = -1
get_obj = get_fvcom(GRID)
url_fvcom = get_obj.get_url(start_time,end_time)
data = get_obj.get_data(url_fvcom)
point = np.vstack((data['nbe'][0].flatten(),data['nbe'][1].flatten(),data['nbe'][2].flatten())).T
wl=[]
for i in point:
    if 0 in i: 
        wl.append(1)
    else:
        wl.append(0)
tf = np.array(wl)
index = np.where(tf==True)
lons = data['lonc'][:][index]
lats = data['latc'][:][index]
print len(lons),type(lons)  #32255 <type 'numpy.ndarray'>
#points['lons'].extend([-70.308555,-70.929282]); points['lats'].extend([42.446686,41.172368])
points['lons'].extend(lons); points['lats'].extend(lats)
fig = plt.figure(figsize=(16,9)) #
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)  # points is using here
ax.plot(lons,lats,'bo',markersize=6)
plt.show()#'''
