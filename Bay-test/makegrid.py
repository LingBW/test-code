#!/usr/bin/python
# Routine to allow users to click on points and return lat,lon lists
# Jim Manning Nov 2014

import sys
from decimal import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
from pylab import ginput

def basemap_region(region):
    path="" # Y:/bathy/"#give the path if these data files are store elsewhere
    #if give the region, choose the filename
    if region=='sne':
        filename='sne_coast.dat'
    if region=='cc':
        filename='capecod_outline.dat'
    if region=='bh':
        filename='bostonharbor_coast.dat'
    if region=='cb':
        filename='cascobay_coast.dat'
    if region=='pb':
        filename='penbay_coast.dat'
    if region=='ma': # mid-atlantic
        filename='necscoast_noaa.dat'
    if region=='ne': # northeast
        filename='necoast_noaa.dat'   
    if region=='wv': # world vec
        filename='necscoast_worldvec.dat'        
    
    #open the data
    f=open(path+filename)

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
        plt.plot(lon_plot,lat_plot,'r') 

def clickmap(n):
   # this allows users to click on a rough map and define lat/lon points
   # where "n" is the number of points
   fig=plt.figure()
   basemap_region('cc')
   pt=fig.ginput(n)
   plt.close('all')
   lon=list(zip(*pt)[0])
   lat=list(zip(*pt)[1])
   return lon,lat

def points_between(st_point,en_point,x):
    """ 
    For 2 positions, interpolate X number of points between them
    where "lat" and "lon" are two element list
    "x" is the number of points wanted between them
    returns lat0,lono
    """
    
    #print st_point,en_point
    lato=[]
    lono=[]
    if not st_point: 
        lato.append(en_point[0]); lono.append(en_point[1])
        return lato,lono
    if not en_point: 
        lato.append(st_point[0]); lono.append(st_point[1])
        return lato,lono
    lati=(en_point[0]-st_point[0])/float(x+1)
    loni=(en_point[1]-st_point[1])/float(x+1)
    for j in range(x+2):
        lato.append(st_point[0]+lati*j)
        lono.append(st_point[1]+loni*j)
    return lato,lono

