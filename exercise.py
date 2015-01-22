
"""
Created on Thu Jan  8 10:18:40 2015

@author: bling
"""

'''import numpy as np
from matplotlib import path
bbox=[-71, -63., 39., 46]
bbox = np.array(bbox)'''
'''   def get_data(self,url):
       
        
      
        #self.data = jata.get_nc_data(url,'lon','lat','latc','lonc',
        self.data = get_nc_data(url,'lon','lat','latc','lonc',
                                     'u','v','siglay','h')
        return self.data  '''
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from M_track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,distance,uniquecolors
from matplotlib import animation
from pandas import Series,DataFrame
start_time = datetime(2015,1,20,0,0,0,0,pytz.UTC)
end_time = datetime(2015,1,21,0,0,0,0,pytz.UTC)
GRID = 'massbay'
DEPTH=-1
MODEL = 'ROMS'#'ROMS',FVCOM
#st_point = [-70.373099,41.905260]
st_point = [41.103188, -71.214276]
if MODEL in ('FVCOM','BOTH'):
    get_obj = get_fvcom(GRID)
    url_fvcom = get_obj.get_url(start_time,end_time)
    #poin = get_obj.get_data(url_fvcom)
    '''lonc = poin['lonc']#.flatten()
    latc = poin['latc']#.flatten()
    lons = poin['lon']#.flatten()
    lats = poin['lat']'''
    point = get_obj.get_track(st_point[1],st_point[0],DEPTH,url_fvcom)
if MODEL in ('ROMS', 'BOTH'):
    get_obj = get_roms()
    url_roms = get_obj.get_url(start_time, end_time)
    #poin = get_obj.get_data(url_roms)
    #lons = poin['lon_rho'][:].flatten()
    #lats = poin['lat_rho'][:].flatten()
    point = get_obj.get_track(st_point[1],st_point[0],DEPTH,url_roms)
##################
#points = {'lats':[39.024946, 41.645052],'lons':[-73.910316, -70.701640]}
points = {'lats':[],'lons':[]}
points['lats'].extend(point['lat']); points['lons'].extend(point['lon'])
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)
ax.plot(point['lon'],point['lat'],'ro',markersize=4) #,label='Startpoint'
#ax.plot(lonc,latc,'bo',markersize=4) #,label='Startpoint'
#point = get_obj.get_data(url_fvcom)
plt.show()
'''lon=-70.183480; lat=41.789235
#if lon<0: lon=lon+360.0 
#if lat<0: lat=-lat            

mapx = Basemap(projection='ortho',lat_0=lat,lon_0=lon,resolution='l')
x,y = mapx(lon,lat)'''
