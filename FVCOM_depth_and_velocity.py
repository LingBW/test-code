# coding: utf-8

# Access data from the NECOFS (New England Coastal Ocean Forecast System) via OPeNDAP
#
# Original code written by Rich Signell and modified by Jim Manning
#
from pylab import *
import matplotlib.tri as Tri
import netCDF4
import datetime as dt

#get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
import numpy as np
#from track_functions import draw_basemap
from mpl_toolkits.basemap import Basemap



bg = 'model' #basemap, model, basemap_region, usgs
parallels_interval=0.02


# MassBay GRID
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'

# GOM3 GRID
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
# 30yr GRID

#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3.nc'
nc = netCDF4.Dataset(url).variables
#nc.keys()
# Desired time for snapshot
start = dt.datetime(2015,12,21,20,0,0)

# Get desired time step  
time_var = nc['time']
itime = netCDF4.date2index(start,time_var,select='nearest')
print 'got nearest time ...'
# Get lon,lat coordinates for nodes (depth)
lat = nc['lat'][:]
lon = nc['lon'][:]
# Get lon,lat coordinates for cell centers (depth)
latc = nc['latc'][:]
lonc = nc['lonc'][:]
# Get Connectivity array
nv = nc['nv'][:].T - 1 #;print nv
# Get depth
h = nc['h'][:]  # depth 
dtime = netCDF4.num2date(time_var[itime],time_var.units)
daystr = dtime.strftime('%Y-%b-%d %H:%M')
print daystr
tri = Tri.Triangulation(lon,lat, triangles=nv)

# get current at layer [0 = surface, -1 = bottom]
ilayer = -1
u = nc['u'][itime, ilayer, :]
v = nc['v'][itime, ilayer, :]
print 'got velocity'
# Which area?
area='Marion_Harbor'
vector_scale=20
if area=='Falmouth':
    levels=arange(-30,2,1)
    size = [-70.6, -70.5, 41.53, 41.6]
    maxvel = 1.0
    subsample = 2
elif area=='Marion_Harbor':
    levels=arange(-8,0,.5)
    size = [-70.77, -70.72, 41.67, 41.72]
    maxvel = .1
    subsample = 1
    vector_scale=3
elif area=='Stellwagen':
    levels=arange(-250,20,1)
    size = [-70.6, -69.95, 42.0, 42.6]
    maxvel = 1.0
    subsample = 2
elif area=='Boston_Harbor':
    levels=arange(-34,2,1)   # depth contours to plot
    size= [-70.97, -70.82, 42.25, 42.35] # 
    maxvel = 0.5
    subsample = 3
print 'got '+area+' to plot'
points = {'lats':[],'lons':[]}  # collect all points we've gained
points['lons'].extend(size[:2]); points['lats'].extend(size[-2:])
# find velocity points in bounding box
ind = argwhere((lonc >= size[0]) & (lonc <= size[1]) & (latc >= size[2]) & (latc <= size[3]))
#size = [min(lonc[ind]),max(lonc[ind]),min(latc[ind]),max(latc[ind])]
#np.random.shuffle(ind)
#Nvec = int(len(ind) / subsample)
#idv = ind[:Nvec]

# tricontourf plot of water depth with vectors on top
fig=plt.figure(figsize=(18,10)) #
ax1 = fig.add_subplot(121)#,aspect=(1.0/cos(mean(lat)*pi/180.0))
ax2 = fig.add_subplot(122)
if bg == 'basemap':
    
    dmap = Basemap(projection='cyl',llcrnrlat=size[2], llcrnrlon=size[0],urcrnrlat=size[3], urcrnrlon=size[1],resolution='f')
    dmap.drawparallels(np.arange(size[2],size[3]+0.01,0.01),labels=[1,0,0,0])
    dmap.drawmeridians(np.arange(size[0],size[1]+0.01,0.01),labels=[0,0,0,1])
    #dmap.drawcoastlines()
    dmap.fillcontinents(color='grey')
    dmap.drawmapboundary()
    dmap.drawlsmask()
    plt.tricontourf(tri, -h,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
    la=plt.colorbar()
    la.set_label('Model Water Depth (m)', rotation=-90)
if bg == 'model':
    #plt.axis(size)
    ax1.patch.set_facecolor('0.5')
    ax1.tricontourf(tri, -h,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
    #plt.colorbar(cs)
    #la=plt.colorbar()
    #la.set_label('Model Water Depth (m)', rotation=-90)
    m = Basemap(projection='cyl',llcrnrlat=size[2],urcrnrlat=size[3],llcrnrlon=size[0],urcrnrlon=size[1],resolution='h',ax=ax1)#,fix_aspect=False)
    m.drawparallels(np.arange(size[2],size[3],parallels_interval),labels=[1,0,0,0],dashes=[2,2],linewidth=1)
    #draw meridians
    m.drawmeridians(np.arange(size[0],size[1],parallels_interval),labels=[0,0,0,1],dashes=[2,2],linewidth=1)
    Q = ax1.quiver(lonc[ind],latc[ind],u[ind],v[ind]) #,scale=vector_scale
    maxstr='%3.1f m/s' % maxvel
    ax1.quiverkey(Q,0.25,0.05,maxvel,maxstr,labelpos='W')
    ax1.set_title('FVCOM Bottom Depths')

if bg =='basemap_region':
    filename='/net/data5/jmanning/bathy/sne_coast.dat'
    f=open(filename)
    lon,lat=[],[]
    for line in f:#read the lat, lon
	    lon.append(line.split()[0])
	    lat.append(line.split()[1])
    nan_location=[]
    # plot the lat,lon between the "nan"
    for i in range(len(lon)):#find "nan" location
        if lon[i]=="nan":
            nan_location.append(i)
    for m in range(1,len(nan_location)):#plot the lat,lon between nan
        lon_plot,lat_plot=[],[]
        for k in range(nan_location[m-1],nan_location[m]):
            lat_plot.append(lat[k])
            lon_plot.append(lon[k])
        plt.plot(lon_plot,lat_plot,'k') 
    plt.axis(size)
    gca().patch.set_facecolor('0.5')
    plt.tricontourf(tri, -h,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
    la=plt.colorbar()
    la.set_label('Model Water Depth (m)', rotation=-90)
    
if bg =='model':
    ss=1
    cont_range = [-3,0]
    draw_parallels = 'ON'
    
    url='http://geoport.whoi.edu/thredds/dodsC/bathy/gom03_v1_0'
    dataset=open_url(url)
    basemap_lat=dataset['lat']
    basemap_lon=dataset['lon']
    basemap_topo=dataset['topo']
    minlat=size[2]
    maxlat=size[3]
    minlon=size[0]
    maxlon=size[1]
    index_minlat=int(round(np.interp(minlat,basemap_lat,range(0,basemap_lat.shape[0]))))-2
    index_maxlat=int(round(np.interp(maxlat,basemap_lat,range(0,basemap_lat.shape[0]))))+2
    index_minlon=int(round(np.interp(minlon,basemap_lon,range(0,basemap_lon.shape[0]))))-2
    index_maxlon=int(round(np.interp(maxlon,basemap_lon,range(0,basemap_lon.shape[0]))))+2
    min_index_lat=min(index_minlat,index_maxlat)
    max_index_lat=max(index_minlat,index_maxlat)
    min_index_lon=min(index_minlon,index_maxlon)
    max_index_lon=max(index_minlon,index_maxlon)
    X,Y=np.meshgrid(basemap_lon[min_index_lon:max_index_lon:ss],basemap_lat[min_index_lat:max_index_lat:ss])
    # You can set negative contours to be solid instead of dashed:
    matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
    # plot the depth
    #print index_minlat,index_maxlat
    #plt.xlim([min(lon),max(lon)])
    #plt.ylim([min(lat),max(lat)])
    #plot the bathy
    #if bathy==True:
    #plt.contourf(X,Y,basemap_topo.topo[min_index_lat:max_index_lat,index_minlon:index_maxlon],[-5000,-1000,-200,-100],colors=['0.75','0.80','0.85','0.90'],linewith=0.05)
    CS=ax2.contourf(X,Y,basemap_topo.topo[min_index_lat:max_index_lat:ss,index_minlon:index_maxlon:ss],np.arange(-8,0,0.5),cmap=plt.cm.gist_earth,linewidths=1)
    #print cont_range
    #CS=plt.contourf(X,Y,basemap_topo.topo[min_index_lat:max_index_lat:ss,index_minlon:index_maxlon:ss],cont_range)#,colors=['0.8'])
    #plt.contour(X,Y,basemap_topo.topo[min_index_lat:max_index_lat:ss,index_minlon:index_maxlon:ss],cont_range,linewidths=2,colors=['cyan','yellow'])
    #plt.contour(X,Y,basemap_topo.topo[min_index_lat:max_index_lat:ss,index_minlon:index_maxlon:ss],range(-30,0,5)
    
    #plt.clabel(cs, fontsize=9, inline=1,fmt='%5.0f'+"m")
    ax2.contourf(X,Y,basemap_topo.topo[min_index_lat:max_index_lat:ss,min_index_lon:max_index_lon:ss],[0,1000],colors='gray')
    m = Basemap(projection='cyl',llcrnrlat=size[2],urcrnrlat=size[3],llcrnrlon=size[0],urcrnrlon=size[1],resolution='h',ax=ax2)#,fix_aspect=False)
    m.drawparallels(np.arange(size[2],size[3],parallels_interval),labels=[0,0,0,0],dashes=[2,2],linewidth=1)
    #draw meridians
    m.drawmeridians(np.arange(size[0],size[1],parallels_interval),labels=[0,0,0,1],dashes=[2,2],linewidth=1)
    Q = ax2.quiver(lonc[ind],latc[ind],u[ind],v[ind]) #,scale=vector_scale
    maxstr='%3.1f m/s' % maxvel
    ax2.quiverkey(Q,0.25,0.05,maxvel,maxstr,labelpos='W')
    ax2.clabel(CS, np.arange(-8,0,0.5)[::16],fontsize=3,fmt='%5.0f', inline=1)
    ax2.set_title('USGS Bottom Depths')
    #ax2.colorbar(CS)

#m = Basemap(projection='cyl',llcrnrlat=size[2],urcrnrlat=size[3],llcrnrlon=size[0],urcrnrlon=size[1],resolution='h',suppress_ticks=True)#,fix_aspect=False)
#m.drawparallels(np.arange(size[2],size[3],parallels_interval),labels=[1,0,0,0],dashes=[2,2],linewidth=1)
#draw meridians
#m.drawmeridians(np.arange(size[0],size[1],parallels_interval),labels=[0,0,0,1],dashes=[2,2],linewidth=1)     
      

#plt.colorbar(CS)
#plt.colorbar(CS, orientation='horizontal', shrink=0.8)
#plt.axis(size)
#plt.xlim(size[:2])
#plt.ylim(size[-2:])
if ilayer==0: 
    layer=' Surface'
elif ilayer==-1:
    layer=' Bottom'
plt.suptitle('%s FVCOM %s Velocity, %s UTC' % (area, layer, daystr));
plt.show()
savefig(area+'_example.png')
