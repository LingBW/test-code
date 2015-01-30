
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
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,distance,uniquecolors
from matplotlib import animation
from pandas import Series,DataFrame
MODEL = 'forecast'
model_points=np.load('model_points.npz')
stp_num = 2; seg_num = 24
lon_set = [[]]*stp_num; lat_set = [[]]*stp_num
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
def animate(n):
    ax.plot(arr_lon[n],arr_lat[n],'ro-',markersize=8,label='forecast')
anim = animation.FuncAnimation(fig, animate, frames=seg_num, interval=50)
plt.legend(loc='lower right',fontsize=10)
###################################################
en_run_time = datetime.now()
#print 'Take '+str(en_run_time-st_run_time)+' run the code. End at '+str(en_run_time) 
anim.save('%s-demo_%s.gif'%(MODEL,en_run_time.strftime("%d-DEC-%H:%M")),
          writer='imagemagick',fps=5,dpi=150) #ffmpeg,imagemagick,mencoder fps=20'''
plt.show()

'''start_time = datetime(2015,1,20,0,0,0,0,pytz.UTC)
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
plt.show()'''
'''lon=-70.183480; lat=41.789235
#if lon<0: lon=lon+360.0 
#if lat<0: lat=-lat            

mapx = Basemap(projection='ortho',lat_0=lat,lon_0=lon,resolution='l')
x,y = mapx(lon,lat)'''
