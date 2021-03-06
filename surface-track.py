import sys
import netCDF4
#import calendar
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
from dateutil.parser import parse
#import pytz
from matplotlib.path import Path
import math
from mpl_toolkits.basemap import Basemap
import colorsys

def distance(lat1, lon1, lat2,lon2):
    """ 
    Calculates both distance and bearing
    note: "origin" and "destintation" are tuples (lat,lon) 
    note: if user inputs lat & lon as degrees-minutes (ddmm.m), it will convert to decimal degrees (dd.dddd)
    """
    #lat1, lon1 = origin
    #lat2, lon2 = destination
    if lat1>1000:
        (lat1,lon1)=dm2dd(lat1,lon1) # this is the conversion from degrees-minutes to decimal degrees
        (lat2,lon2)=dm2dd(lat2,lon2)
        print 'converted to from ddmm to dd.ddd'
    radius = 6371 # km
    

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    
    '''def calcBearing(lat1, lon1, lat2, lon2):
       dLon = lon2 - lon1
       y = math.sin(dLon) * math.cos(lat2)
       x = math.cos(lat1) * math.sin(lat2) \
           - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
       return math.atan2(y, x)
       
    bear= math.degrees(calcBearing(lat1, lon1, lat2, lon2))'''  
    return d

def dm2dd(lat,lon):
    """
    convert lat, lon from decimal degrees,minutes to decimal degrees
    """
    (a,b)=divmod(float(lat),100.)   
    aa=int(a)
    bb=float(b)
    lat_value=aa+bb/60.

    if float(lon)<0:
        (c,d)=divmod(abs(float(lon)),100.)
        cc=int(c)
        dd=float(d)
        lon_value=cc+(dd/60.)
        lon_value=-lon_value
    else:
        (c,d)=divmod(float(lon),100.)
        cc=int(c)
        dd=float(d)
        lon_value=cc+(dd/60.)
    return lat_value, -lon_value
def getrawdrift(did,filename):
    '''
    routine to get raw drifter data from ascii files posted on the web
    '''
    url='http://nefsc.noaa.gov/drifter/'+filename
    df=pd.read_csv(url,header=None, delimiter="\s+")
    # make a datetime
    dtime=[]
    index = np.where(df[0]==int(did))[0]
    newData = df.ix[index]
    for k in newData[0].index:
        dt1=datetime(2015, newData[2][k],newData[3][k],newData[4][k],newData[5][k])
        dtime.append(dt1)
    #print dtime
    return newData[8],newData[7],dtime,newData[9] # lat,lon,time,

def getdrift(did):
    """
    routine to get drifter data from archive based on drifter id (did)
    -assumes "import pandas as pd" has been issued above
    -get remotely-stored drifter data via ERDDAP
    -input: deployment id ("did") number where "did" is a string
    -output: time(datetime), lat (decimal degrees), lon (decimal degrees), depth (meters)
    
    note: there is another function below called "data_extracted" that does a similar thing returning a dictionary
    
    Jim Manning June 2014
    """
    url = 'http://comet.nefsc.noaa.gov:8080/erddap/tabledap/drifters.csv?time,latitude,longitude,depth&id="'+did+'"&orderBy("time")'
    df=pd.read_csv(url,skiprows=[1]) #returns a dataframe with all that requested
    #print df    
    # generate this datetime 
    for k in range(len(df)):
       df.time[k]=parse(df.time[k]) # note this "parse" routine magically converts ERDDAP time to Python datetime
    return df.latitude.values,df.longitude.values,df.time.values,df.depth.values  

def get_nc_data(url, *args):
    '''
    get specific dataset from url

    *args: dataset name, composed by strings
    ----------------------------------------
    example:
        url = 'http://www.nefsc.noaa.gov/drifter/drift_tcs_2013_1.dat'
        data = get_url_data(url, 'u', 'v')
    '''
    nc = netCDF4.Dataset(url)
    data = {}
    for arg in args:
        try:
            data[arg] = nc.variables[arg]
        except (IndexError, NameError, KeyError):
            print 'Dataset {0} is not found'.format(arg)
    return data

def input_with_default(data, v_default):
    '''
    data: string, could be name of value you want to get
    v_default
    '''
    l = (data, str(v_default))
    try:
        data_input = input('Please input %s(default %s)(If don\'t want to make change, press "Enter"): ' % l)
    except SyntaxError:
        data_output = v_default
    else:
        data_output = data_input
    return data_output
    
def shrink(a,b):
    """Return array shrunk to fit a specified shape by triming or averaging.
    
    a = shrink(array, shape)
    
    array is an numpy ndarray, and shape is a tuple (e.g., from
    array.shape). a is the input array shrunk such that its maximum
    dimensions are given by shape. If shape has more dimensions than
    array, the last dimensions of shape are fit.
    
    as, bs = shrink(a, b)
    
    If the second argument is also an array, both a and b are shrunk to
    the dimensions of each other. The input arrays must have the same
    number of dimensions, and the resulting arrays will have the same
    shape.
    Example
    -------
    
    >>> shrink(rand(10, 10), (5, 9, 18)).shape
    (9, 10)
    >>> map(shape, shrink(rand(10, 10, 10), rand(5, 9, 18)))        
    [(5, 9, 10), (5, 9, 10)]   
       
    """

    if isinstance(b, np.ndarray):
        if not len(a.shape) == len(b.shape):
            raise Exception, \
                  'input arrays must have the same number of dimensions'
        a = shrink(a,b.shape)
        b = shrink(b,a.shape)
        return (a, b)

    if isinstance(b, int):
        b = (b,)

    if len(a.shape) == 1:                # 1D array is a special case
        dim = b[-1]
        while a.shape[0] > dim:          # only shrink a
#            if (dim - a.shape[0]) >= 2:  # trim off edges evenly
            if (a.shape[0] - dim) >= 2:
                a = a[1:-1]
            else:                        # or average adjacent cells
                a = 0.5*(a[1:] + a[:-1])
    else:
        for dim_idx in range(-(len(a.shape)),0):
            dim = b[dim_idx]
            a = a.swapaxes(0,dim_idx)        # put working dim first
            while a.shape[0] > dim:          # only shrink a
                if (a.shape[0] - dim) >= 2:  # trim off edges evenly
                    a = a[1:-1,:]
                if (a.shape[0] - dim) == 1:  # or average adjacent cells
                    a = 0.5*(a[1:,:] + a[:-1,:])
            a = a.swapaxes(0,dim_idx)        # swap working dim back
    return a

def data_extracted(filename,drifter_id=None,starttime=None):
    '''
    get a dictionary called "data" made of time, lon, lat from local file.
    filename: local file diretory
    drifter_id: the specific data of some id you want.
    starttime: have to be input with drifter_id, or just drifter_id.
    '''
    data = {}
    did, dtime, dlon, dlat = [], [], [], []
    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                line = line.split()
                did.append(int(line[0]))
                dtime.append(datetime(year=2013,
                                      month=int(line[2]),day=int(line[3]),
                                      hour=int(line[4]),minute=int(line[5])))
                dlon.append(float(line[7]))
                dlat.append(float(line[8]))
            except IndexError:
                continue
    if drifter_id is not None:
        i = index_of_value(did, drifter_id)
        if starttime is not None:
            dtime_temp = dtime[i[0]:i[-1]+1]
            j = index_of_value(dtime_temp, starttime)
            data['time'] = dtime[i[0]:i[-1]+1][j[0]:]
            data['lon'] = dlon[i[0]:i[-1]+1][j[0]:]
            data['lat'] = dlat[i[0]:i[-1]+1][j[0]:]
        else:
            data['time'] = dtime[i[0]:i[-1]+1]
            data['lon'] = dlon[i[0]:i[-1]+1]
            data['lat'] = dlat[i[0]:i[-1]+1]
    elif drifter_id is None and starttime is None:
        data['time'] = dtime
        data['lon'] = dlon
        data['lat'] = dlat
    else:
        raise ValueError("Please input drifter_id while starttime is input")
    return data

def index_of_value(dlist,dvalue):
    '''
    return the indices of dlist that equals dvalue
    '''
    index = []
    startindex = dlist.index(dvalue)
    i = startindex
    for v in dlist[startindex:]:
        if v == dvalue:
            index.append(i)
        i+=1
    return index

class track(object):
    def __init__(self, startpoint):
        '''
        gets the start point of the water, and the location of datafile.
        '''
        self.startpoint = startpoint
        
    def get_data(self, url):
        '''
        calls get_data
        '''        
        pass                                 
        
    def nearest_point_index(self, lon, lat, lons, lats,rad):  #,num=4
        '''
        Return the nearest point(lonp,latp) and distance to origin point(lon,lat).
        lon, lat: the coordinate of start point, float
        latp, lonp: the coordinate of points to be calculated.
        '''
        def bbox2ij(lon, lat, lons, lats, rad):  
            
            '''bbox = [lon-length, lon+length, lat-length, lat+length]
            bbox = np.array(bbox)
            mypath = np.array([bbox[[0,1,1,0]],bbox[[2,2,3,3]]]).T#'''
            p = Path.circle((lon,lat),radius=rad)
            points = np.vstack((lons,lats)).T  #numpy.vstack(tup):Stack arrays in sequence vertically
            #print 'lons',lons
            #tshape = np.shape(lons)
            
            inside = []
            
            for i in range(len(points)):
                inside.append(p.contains_point(points[i]))  # .contains_point return 0 or 1
                
            sidex = np.array(inside, dtype=bool)#.reshape(tshape)
            index = np.where(sidex==True)
            
            '''check if there are no points inside the given area'''        
            
            if not index[0].tolist():          # bbox covers no area
                print 'This point is out of the model area.'
                raise Exception()
                
            else:
                return index        
        
        def min_distance(lon,lat,lons,lats):
            '''Find out the nearest distance to (lon,lat),and return lon.distance units: meters'''
            #mapx = Basemap(projection='ortho',lat_0=lat,lon_0=lon,resolution='l')
            dis_set = []
            #x,y = mapx(lon,lat)
            for i,j in zip(lons,lats):
                #x2,y2 = mapx(i,j)
                ss=math.sqrt((lon-i)**2+(lat-j)**2)
                #ss=math.sqrt((x-x2)**2+(y-y2)**2)
                dis_set.append(ss)
            dis = min(dis_set)
            p = dis_set.index(dis)
            lonp = lons[p]; latp = lats[p]
            return lonp,latp,dis       
        index = bbox2ij(lon, lat, lons, lats,rad)
        lon_covered = lons[index];  lat_covered = lats[index]       
        lonp,latp,distance = min_distance(lon,lat,lon_covered,lat_covered)
        #index1 = np.where(lons==lonp)
        #index2 = np.where(lats==latp)
        #index = np.intersect1d(index1,index2)        
        #points = np.vstack((lons.flatten(),lats.flatten())).T 
        #index = [i for i in xrange(len(points)) if ([lonp,latp]==points[i]).all()]
        '''index = []
        for i in len(points):
            if np.all([[lonp,latp],points[i]]):
                index.append(i)'''
                
        #index = np.where(points==[lonp,latp])
        #print 'index',index
        return lonp,latp,distance  #,lonp,latp
        
    def get_track(self, timeperiod, data):
        pass
    
class get_roms(track):
    '''
    ####(2009.10.11, 2013.05.19):version1(old) 2009-2013
    ####(2013.05.19, present): version2(new) 2013-present
    (2006.01.01 01:00, 2014.1.1 00:00)
    '''
    
    def __init__(self):
        pass
    
    def nearest_point(self, lon, lat, lons, lats, length=0.06):  #0.3/5==0.06
        '''Find the nearest point to (lon,lat) from (lons,lats),
           return the nearest-point (lon,lat)
           author: Bingwei'''
        p = Path.circle((lon,lat),radius=length)
        #numpy.vstack(tup):Stack arrays in sequence vertically
        points = np.vstack((lons.flatten(),lats.flatten())).T  
        
        insidep = []
        #collect the points included in Path.
        for i in xrange(len(points)):
            if p.contains_point(points[i]):# .contains_point return 0 or 1
                insidep.append(points[i])  
        # if insidep is null, there is no point in the path.
        if not insidep:
            print 'There is no model-point near the given-point.'
            raise Exception()
        #calculate the distance of every points in insidep to (lon,lat)
        distancelist = []
        for i in insidep:
            ss=math.sqrt((lon-i[0])**2+(lat-i[1])**2)
            distancelist.append(ss)
        # find index of the min-distance
        mindex = np.argmin(distancelist)
        # location the point
        lonp = insidep[mindex][0]; latp = insidep[mindex][1]
        
        return lonp,latp
        
    def mnearest_point(self, lon, lat, lons, lats, length=0.06):  #0.3/5==0.06
        '''Find the nearest point to (lon,lat) from (lons,lats),
           return the nearest-point (lon,lat)
           author: Bingwei'''
        p = Path.circle((lon,lat),radius=length)
        #numpy.vstack(tup):Stack arrays in sequence vertically
        points = np.vstack((lons,lats)).T  
        
        insidep = []
        #collect the points included in Path.
        for i in xrange(len(points)):
            if p.contains_point(points[i]):# .contains_point return 0 or 1
                insidep.append(points[i])  
        # if insidep is null, there is no point in the path.
        if not insidep:
            print 'There is no model-point near the given-point.'
            raise Exception()
        #calculate the distance of every points in insidep to (lon,lat)
        distancelist = []
        for i in insidep:
            ss=math.sqrt((lon-i[0])**2+(lat-i[1])**2)
            distancelist.append(ss)
        # find index of the min-distance
        mindex = np.argmin(distancelist)
        # location the point
        lonp = insidep[mindex][0]; latp = insidep[mindex][1]
        
        return lonp,latp
        
    def get_url(self, starttime, endtime):
        '''
        get url according to starttime and endtime.
        '''
        starttime = starttime
        self.hours = int((endtime-starttime).total_seconds()/60/60) # get total hours
        # time_r = datetime(year=2006,month=1,day=9,hour=1,minute=0)
        
        url_oceantime = '''http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best?time'''
        url = """http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best?h[0:1:81][0:1:129],
        mask_rho[0:1:81][0:1:128],mask_u[0:1:81][0:1:128],mask_v[0:1:80][0:1:129],zeta[{0}:1:{1}][0:1:81][0:1:129],u[{0}:1:{1}][0:1:35][0:1:81][0:1:128],
        v[{0}:1:{1}][0:1:35][0:1:80][0:1:129],s_rho[0:1:35],lon_rho[0:1:81][0:1:129],lat_rho[0:1:81][0:1:129],lon_u[0:1:81][0:1:128],lat_u[0:1:81][0:1:128],
        lon_v[0:1:80][0:1:129],lat_v[0:1:80][0:1:129],time[0:1:19523]"""
        try:
            oceantime = netCDF4.Dataset(url_oceantime).variables['time'][:]
            self.oceantime = oceantime
        except:
            print 'ROMS database is unavailable!'
            raise Exception()
        # get model works time horizon(UTC).
        fmodtime = datetime(2013,05,18) + timedelta(hours=float(oceantime[0]))
        emodtime = datetime(2013,05,18) + timedelta(hours=float(oceantime[-1]))
        mstt = fmodtime.strftime('%m/%d/%Y %H:%M') #model start time
        mett = emodtime.strftime('%m/%d/%Y %H:%M') #model end time
        # get number of hour from 05/18/2013
        t1 = (starttime - datetime(2013,05,18)).total_seconds()/3600 
        t2 = (endtime - datetime(2013,05,18)).total_seconds()/3600
        #t1 = int(round(t1)); t2 = int(round(t2))
        # judge if the starttime and endtime in the model time horizon
        print starttime, endtime
        if starttime<fmodtime or starttime>emodtime or endtime<fmodtime or endtime>emodtime:
            print 'Time: Error! Model(ROMS) only works between %s with %s.'%(mstt,mett)
            raise Exception()
        #index1 = np.where(oceantime==t1)[0][0]; #print index1
        #index2 = np.where(oceantime==t2)[0][0]; #print index2
        int1 = oceantime - t1; int2 = oceantime - t2
        index1 = np.argmin(abs(int1)); index2 = np.argmin(abs(int2))
        url = url.format(index1, index2)
        self.url=url
        
        return url
    
    def shrink_data(self,lon,lat,lons,lats):
        lont = []; latt = []
        p = Path.circle((lon,lat),radius=0.6)
        pints = np.vstack((lons.flatten(),lats.flatten())).T
        for i in range(len(pints)):
            if p.contains_point(pints[i]):
                lont.append(pints[i][0])
                latt.append(pints[i][1])
        lonl=np.array(lont); latl=np.array(latt)#'''
        if not lont:
            print 'point position error! shrink_data'
            sys.exit()
        return lonl,latl
    
    def mshrink_data(self,lon,lat,lons,lats):
        # ind = argwhere((lonc >= size[0]) & (lonc <= size[1]) & (latc >= size[2]) & (latc <= size[3]))
        sz = 0.04; #lonl,latl = [],[]
        mlon = lon+sz; nlon = lon-sz
        mlat = lat+sz; nlat = lat-sz
        ind = np.argwhere((lons >= nlon) & (lons <= mlon) & (lats >= nlat) & (lats <= mlat)); #print type(ind),ind
        if not len(ind):
            print 'point position error! shrink_data'
            raise Exception()
            #sys.exit()
        '''for i in ind:
            lonl.append(lons[i[0],i[1]]); latl.append(lats[i[0],i[1]])
        plt.plot(lonl,latl)       
        plt.plot(lon,lat,'ro-')
        plt.show()#'''
        return ind
        
    def get_data(self, url):
        '''
        return the data needed.
        url is from get_roms.get_url(starttime, endtime)
        '''
        data = get_nc_data(url, 'lon_rho','lat_rho','lon_u','lat_u','lon_v','lat_v','mask_rho','mask_u','mask_v','u','v','h','s_rho','zeta')
        self.lon_rho = data['lon_rho'][:]; self.lat_rho = data['lat_rho'][:] 
        self.lon_u,self.lat_u = data['lon_u'][:], data['lat_u'][:]
        self.lon_v,self.lat_v = data['lon_v'][:], data['lat_v'][:]
        self.h = data['h'][:]; self.s_rho = data['s_rho'][:]
        self.mask_u = data['mask_u'][:]; self.mask_v = data['mask_v'][:]#; mask_rho = data['mask_rho'][:]
        self.u = data['u']; self.v = data['v']; self.zeta = data['zeta']
        np.savez('ROMS_basic_data.npz', lon_u=self.lon_u, lat_u=self.lat_u, lon_v=self.lon_v, lat_v=self.lat_v, mask_u=self.mask_u, mask_v=self.mask_v)
        #np.savez('ROMS_realtime_data.npz', u=self.u, v=self.v, oceantime=self.oceantime)       
        #return self.fmodtime, self.emodtime
        
    def sf_get_data(self, url):
        '''
        return the data needed.
        url is from get_roms.get_url(starttime, endtime)
        '''
        data = np.load('ROMS_basic_data.npz')
        #self.lon_rho = data['lon_rho'][:]; self.lat_rho = data['lat_rho'][:] 
        self.lon_u,self.lat_u = data['lon_u'], data['lat_u']
        self.lon_v,self.lat_v = data['lon_v'], data['lat_v']
        #self.h = data['h'][:]; self.s_rho = data['s_rho'][:]
        self.mask_u = data['mask_u']; self.mask_v = data['mask_v']#; mask_rho = data['mask_rho'][:]
        #np.savez('ROMS_basic_data.npz',lon_u=self.lon_u, lat_u=self.lat_u, lon_v=self.lon_v, lat_v=self.lat_v, mask_u=self.mask_u, mask_v=self.mask_v)
        data = get_nc_data(url, 'u','v')        
        self.u = data['u']; self.v = data['v']; #self.zeta = data['zeta']
        #return self.fmodtime, self.emodtime
        
    

    def sf_get_track(self,lon,lat,depth,track_way):#, depth
        '''
        get the nodes of specific time period
        lon, lat: start point
        depth: 0~35, the 0th is the bottom.
        '''
        
        #lonrho,latrho = self.shrink_data(lon,lat,self.lon_rho,self.lat_rho)
        #lonu,latu = self.mshrink_data(lon,lat,self.lon_u,self.lat_u)
        #lonv,latv = self.mshrink_data(lon,lat,self.lon_v,self.lat_v)
        nodes = dict(lon=[lon], lat=[lat])

        t = abs(self.hours); print 'hour',t
        for j in xrange(t):  #Roms points update every 2 hour
            #lonrp,latrp = self.nearest_point(lon,lat,lonrho,latrho)
            '''lonup,latup = self.mnearest_point(lon,lat,lonu,latu)
            lonvp,latvp = self.mnearest_point(lon,lat,lonv,latv)
            indexu = np.where(self.lon_u==lonup)
            indexv = np.where(self.lon_v==lonvp)#'''
            #indexr = np.where(self.lon_rho==lonrp)
            try:
                indexu = self.mshrink_data(lon,lat,self.lon_u,self.lat_u);#print 'len(indexu)==',len(indexu),indexu[0]
                indexv = self.mshrink_data(lon,lat,self.lon_v,self.lat_v)
            except:
                raise
                #return nodes
            us,vs = [],[];layer = 35
            for i in indexu:
                if not self.mask_u[i[0],i[1]]:
                    print 'No u velocity.'
                    raise Exception()
                #print i[0],i[1]
                ut = self.u[j,layer][i[0],i[1]]; print 'ut:',ut #[i[0],i[1]]
                us.append(ut)
            for i in indexv:
                if not self.mask_v[i[0],i[1]]:
                    print 'No v velocity'
                    raise Exception()
                vt = self.v[j,layer][i[0],i[1]]; print 'ut:',ut
                vs.append(vt)
            #print us, len(us)
            u_t = np.mean(us); v_t = np.mean(vs)
            #u_t = sum(us) / float(len(us)); v_t = sum(vs) / float(len(vs))
            dx = 60*60*u_t; dy = 60*60*v_t#float(v_p)
            lon = lon + dx/(111111*np.cos(lat*np.pi/180))
            lat = lat + dy/111111
            print j,lat,lon
            nodes['lon'].append(lon);nodes['lat'].append(lat)
        
        return nodes
            
        
        
class get_fvcom(track):
    def __init__(self, mod):
        self.modelname = mod
            
    def nearest_point(self, lon, lat, lons, lats, length):  #0.3/5==0.06
        '''Find the nearest point to (lon,lat) from (lons,lats),
           return the nearest-point (lon,lat)
           author: Bingwei'''
        p = Path.circle((lon,lat),radius=length)
        #numpy.vstack(tup):Stack arrays in sequence vertically
        points = np.vstack((lons.flatten(),lats.flatten())).T  
        
        insidep = []
        #collect the points included in Path.
        for i in xrange(len(points)):
            if p.contains_point(points[i]):# .contains_point return 0 or 1
                insidep.append(points[i])  
        # if insidep is null, there is no point in the path.
        if not insidep:
            print 'There is no model-point near the given-point.'
            raise Exception()
        #calculate the distance of every points in insidep to (lon,lat)
        distancelist = []
        for i in insidep:
            ss=math.sqrt((lon-i[0])**2+(lat-i[1])**2)
            distancelist.append(ss)
        # find index of the min-distance
        mindex = np.argmin(distancelist)
        # location the point
        lonp = insidep[mindex][0]; latp = insidep[mindex][1]
        
        return lonp,latp
        
    def get_data(self, starttime, endtime):
        '''
        get different url according to starttime and endtime.
        urls are monthly.
        '''
        
        self.hours = int(round((endtime-starttime).total_seconds()/60/60))
                
        if self.modelname == "GOM3":
            self.realdata = np.load('FVCOM_GOM3_realtime_data.npz')
            self.basicdata = np.load('FVCOM_GOM3_basic_data.npz')
            '''try:
                mTime = self.realdata['Times'][:]              
            except:
                print '"GOM3" database is unavailable!'
                raise Exception() #'''
            mTime = self.realdata['Times'][:]
            Times = []
            for i in mTime:
                strt = '201'+i[3]+'-'+i[5]+i[6]+'-'+i[8]+i[9]+' '+i[11]+i[12]+':'+i[14]+i[15]
                Times.append(datetime.strptime(strt,'%Y-%m-%d %H:%M'))
            fmodtime = Times[0]; emodtime = Times[-1]         
            if starttime<fmodtime or starttime>emodtime or endtime<fmodtime or endtime>emodtime:
                print 'Time: Error! Model(GOM3) only works between %s with %s(UTC).'%(fmodtime,emodtime)
                raise Exception()
            self.b_points = np.load('Boundary_points_GOM3.npy')
                       
        elif self.modelname == "massbay":
            self.realdata = np.load('FVCOM_massbay_realtime_data.npz')
            self.basicdata = np.load('FVCOM_massbay_basic_data.npz')
            '''try:
                mTime = self.realdata['Times'][:]              
            except:
                print '"massbay" database is unavailable!'
                raise Exception()#'''
            mTime = self.realdata['Times'][:]
            Times = []
            for i in mTime:
                strt = '201'+i[3]+'-'+i[5]+i[6]+'-'+i[8]+i[9]+' '+i[11]+i[12]+':'+i[14]+i[15]
                Times.append(datetime.strptime(strt,'%Y-%m-%d %H:%M'))
            fmodtime = Times[0]; emodtime = Times[-1]         
            if starttime<fmodtime or starttime>emodtime or endtime<fmodtime or endtime>emodtime:
                print 'Time: Error! Model(massbay) only works between %s with %s(UTC).'%(fmodtime,emodtime)
                raise Exception()
            self.b_points = np.load('Boundary_points_GOM3.npy')
            
        elif self.modelname == "30yr": #start at 1977/12/31 23:00, end at 2014/1/1 0:0, time units:hours
            timeurl = """http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3?time[0:1:316008]"""
            url = '''http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3?h[0:1:48450],
            lat[0:1:48450],latc[0:1:90414],lon[0:1:48450],lonc[0:1:90414],nbe[0:1:2][0:1:90414],siglay[0:1:44][0:1:48450],
            u[{0}:1:{1}][0:1:44][0:1:90414],v[{0}:1:{1}][0:1:44][0:1:90414],zeta[{0}:1:{1}][0:1:48450]'''
            
            try:
                mtime = netCDF4.Dataset(timeurl).variables['time'][:]
            except:
                print '"30yr" database is unavailable!'
                raise Exception
            # get model's time horizon(UTC).
            '''fmodtime = datetime(1858,11,17) + timedelta(float(mtime[0]))
            emodtime = datetime(1858,11,17) + timedelta(float(mtime[-1]))
            mstt = fmodtime.strftime('%m/%d/%Y %H:%M')
            mett = emodtime.strftime('%m/%d/%Y %H:%M') #'''
            # get number of days from 11/17/1858
            t1 = (starttime - datetime(1858,11,17)).total_seconds()/86400 
            t2 = (endtime - datetime(1858,11,17)).total_seconds()/86400
            if not mtime[0]<t1<mtime[-1] or not mtime[0]<t2<mtime[-1]:
                #print 'Time: Error! Model(massbay) only works between %s with %s(UTC).'%(mstt,mett)
                print 'Time: Error! Model(massbay) only works between 1978-1-1 with 2014-1-1(UTC).'
                raise Exception()
            
            tm1 = mtime-t1; #tm2 = mtime-t2
            index1 = np.argmin(abs(tm1)); #index2 = np.argmin(abs(tm2)); print index1,index2
            index2 = index1 + self.hours
            url = url.format(index1, index2)
            Times = []
            for i in range(self.hours+1):
                Times.append(starttime+timedelta(i))
            self.mTime = Times
            self.url = url
        #print url
        npTimes = np.array(Times)
        tm1 = npTimes-starttime; #tm2 = mtime-t2
        index1 = np.argmin(abs(tm1))
        index2 = index1 + self.hours + 1 #'''
        self.mTime = Times[index1:index2]
        
        self.u = self.realdata['u'][index1:index2]; self.v = self.realdata['v'][index1:index2]; 
        #self.zeta = self.realdata['zeta'][index1:index2]
        
        self.lonc, self.latc = self.basicdata['lonc'], self.basicdata['latc']  #quantity:165095
        self.lons, self.lats = self.basicdata['lon'], self.basicdata['lat']
        #self.h = self.basicdata['h']; self.siglay = self.basicdata['siglay']
        '''nbe1=self.basicdata['nbe'][0];nbe2=self.basicdata['nbe'][1];
        nbe3=self.basicdata['nbe'][2]
        pointt = np.vstack((nbe1,nbe2,nbe3)).T; self.pointt = pointt
        wl=[]
        for i in pointt:
            if 0 in i: 
                wl.append(1)
            else:
                wl.append(0)
        self.wl = wl
        tf = np.array(wl)
        inde = np.where(tf==True)
        #b_index = inde[0]
        lonb = self.lonc[inde]; latb = self.latc[inde]        
        self.b_points = np.vstack((lonb,latb)).T
        np.save('Boundary_points_massbay',self.b_points)#'''
        
        #self.b_points = np.load('Boundary_points_massbay.npy')
        
        return self.b_points
        
    def shrink_data(self,lon,lat,lons,lats,rad):
        lont = []; latt = []
        p = Path.circle((lon,lat),radius=rad)
        pints = np.vstack((lons,lats)).T
        for i in range(len(pints)):
            if p.contains_point(pints[i]):
                lont.append(pints[i][0])
                latt.append(pints[i][1])
        lonl=np.array(lont); latl=np.array(latt)#'''
        if not lont:
            print 'point position error! shrink_data'
            sys.exit()
        return lonl,latl
   
    def eline_path(self,lon,lat):
        '''
        When drifter close to boundary(less than 0.1),find one nearest point to drifter from boundary points, 
        then find two nearest boundary points to previous boundary point, create a boundary path using that 
        three boundary points.
        '''
        def boundary_location(locindex,pointt,wl):
            '''
            Return the index of boundary points nearest to 'locindex'.
            '''
            loca = []
            dx = pointt[locindex]; #print 'func',dx 
            for i in dx: # i is a number.
                #print i  
                if i ==0 :
                    continue
                dx1 = pointt[i-1]; #print dx1
                if 0 in dx1:
                    loca.append(i-1)
                else:
                    for j in dx1:
                        if j != locindex+1:
                            if wl[j-1] == 1:
                                loca.append(j-1)
            return loca
        
        p = Path.circle((lon,lat),radius=0.02) #0.06
        dis = []; bps = []; pa = []
        tlons = []; tlats = []; loca = []
        for i in self.b_points:
            if p.contains_point(i):
                bps.append((i[0],i[1]))
                d = math.sqrt((lon-i[0])**2+(lat-i[1])**2)
                dis.append(d)
        bps = np.array(bps)
        if not dis:
            return None
        else:
            print "Close to boundary."
            dnp = np.array(dis)
            dmin = np.argmin(dnp)
            lonp = bps[dmin][0]; latp = bps[dmin][1]
            index1 = np.where(self.lonc==lonp)
            index2 = np.where(self.latc==latp)
            elementindex = np.intersect1d(index1,index2)[0] # location 753'''
            #print index1,index2,elementindex  
            loc1 = boundary_location(elementindex,self.pointt,self.wl) ; #print 'loc1',loc1
            loca.extend(loc1)
            loca.insert(1,elementindex)               
            for i in range(len(loc1)):
                loc2 = boundary_location(loc1[i],self.pointt,self.wl); #print 'loc2',loc2
                if len(loc2)==1:
                    continue
                for j in loc2:
                    if j != elementindex:
                        if i ==0:
                            loca.insert(0,j)
                        else:
                            loca.append(j)
            
            for i in loca:
                tlons.append(self.lonc[i]); tlats.append(self.latc[i])
                       
            for i in xrange(len(tlons)):
                pa.append((tlons[i],tlats[i]))
            #path = Path(pa)#,codes
            return pa
        
    def uvt(self,u1,v1,u2,v2):
        t = 2
        a=0; b=0
        if u1==u2:
            a = u1
        else:
            ut = np.arange(u1,u2,float(u2-u1)/t)
            for i in ut:
                a += i
            a = a/t  
        
        if v1==v2:
            b = v1
        else:
            c = float(v2-v1)/t
            vt = np.arange(v1,v2,c)
            for i in vt:
                b += i
            b = b/t
               
        return a, b
        
    def get_track(self,lon,lat,track_way): #,b_index,nvdepth, 
        '''
        Get forecast points start at lon,lat
        '''
        modpts = dict(lon=[lon], lat=[lat], layer=[], time=[]) #model forecast points
        #uvz = netCDF4.Dataset(self.url)
        #u = uvz.variables['u']; v = uvz.variables['v']; zeta = uvz.variables['zeta']
        #print 'len u',len(u)
        if lon>90:
            lon, lat = dm2dd(lon, lat)
        lonl,latl = self.shrink_data(lon,lat,self.lonc,self.latc,0.5)
        #lonk,latk = self.shrink_data(lon,lat,self.lons,self.lats,0.5)
        try:
            if self.modelname == "GOM3" or self.modelname == "30yr":
                lonp,latp = self.nearest_point(lon, lat, lonl, latl,0.2)
                #lonn,latn = self.nearest_point(lon,lat,lonk,latk,0.3)
            if self.modelname == "massbay":
                lonp,latp = self.nearest_point(lon, lat, lonl, latl,0.03)
                #lonn,latn = self.nearest_point(lon,lat,lonk,latk,0.05)        
            index1 = np.where(self.lonc==lonp)
            index2 = np.where(self.latc==latp)
            elementindex = np.intersect1d(index1,index2)
            #index3 = np.where(self.lons==lonn)
            #index4 = np.where(self.lats==latn)
            #nodeindex = np.intersect1d(index3,index4); #print nodeindex
            ################## boundary 1 ####################
            pa = self.eline_path(lon,lat); #print 'path'
            ################## boundary 2 ####################
            '''if elementindex in b_index:
                print 'boundary'
                dss=math.sqrt((lonp-lonn)**2+(latp-latn)**2)
                pa = Path.circle((lonp,latp),radius=dss)
                if not pa.contains_point([lon,lat]):
                    print 'Sorry, point on the land here.Depends on Boundarypoint'
                    raise Exception()#
            else :
                pa = self.boundary_path(lon,lat)#'''   
            ################## boundary 3 ####################
            '''if elementindex in b_index:
                #if ([lonp,latp]==i).all():               
                nod = nv[:,elementindex]; 
                if not (nodeindex+1) in nod:
                    print 'Sorry, point on the land here.Depends on Boundarypoint'
                    raise Exception()#
                else :
                    dss=math.sqrt((lonp-lonn)**2+(latp-latn)**2)
                    if distance>dss:               
                        print 'Sorry, point on the land here.Depends on Boundarypoint'
                        raise Exception()#'''
            
            '''if track_way=='backward' : # backwards case
                waterdepth = self.h[nodeindex]+self.zeta[-1,nodeindex]
                modpts['time'].append(self.mTime[-1])
            else:
                waterdepth = self.h[nodeindex]+self.zeta[0,nodeindex]
                modpts['time'].append(self.mTime[0])
            depth_total = self.siglay[:,nodeindex]*waterdepth  
            layer = np.argmin(abs(depth_total+depth)); #print 'layer',layer
            modpts['layer'].append(layer); 
            if waterdepth<(abs(depth)): 
                print 'This point is too shallow.Less than %d meter.'%abs(depth)
                raise Exception()#'''
        except:
            print 'Here 1'
            return modpts,0  
            
        t = abs(self.hours)         
        for i in xrange(t):            
            if i!=0 and i%24==0 :
                #print 'layer,lon,lat,i',layer,lon,lat,i
                lonl,latl = self.shrink_data(lon,lat,self.lonc,self.latc,0.5)
                #lonk,latk = self.shrink_data(lon,lat,self.lons,self.lats,0.5)
            if track_way=='backward' : # backwards case
                u_t1 = self.u[t-i,elementindex][0]*(-1); v_t1 = self.v[t-i,elementindex][0]*(-1)
                u_t2 = self.u[t-i-1,elementindex][0]*(-1); v_t2 = self.v[t-i-1,elementindex][0]*(-1)
            else:
                u_t1 = self.u[i,elementindex][0]; v_t1 = self.v[i,elementindex][0]
                u_t2 = self.u[i+1,elementindex][0]; v_t2 = self.v[i+1,elementindex][0]
            u_t,v_t = self.uvt(u_t1,v_t1,u_t2,v_t2)
            #u_t = (u_t1+u_t2)/2; v_t = (v_t1+v_t2)/2
            '''if u_t==0 and v_t==0: #There is no water
                print 'Sorry, hits the land,u,v==0'
                return modpts,1 #'''
            #print "u[i,layer,elementindex]",u[i,layer,elementindex]
            dx = 60*60*u_t; dy = 60*60*v_t
            #mapx = Basemap(projection='ortho',lat_0=lat,lon_0=lon,resolution='l')                        
            #x,y = mapx(lon,lat)
            #temlon,temlat = mapx(x+dx,y+dy,inverse=True)            
            temlon = lon + (dx/(111111*np.cos(lat*np.pi/180)))
            temlat = lat + dy/111111 #'''
            #########case for boundary 1 #############
            if pa:
                teml = [(lon,lat),(temlon,temlat)]
                tempa = Path(teml)
                if pa.intersects_path(tempa): 
                    print 'Sorry, point hits land here.path'
                    return modpts,1 #'''
                
            #########case for boundary 2 #############
            '''if pa :
                if not pa.contains_point([temlon,temlat]):
                    print 'Sorry, point hits land here.path'
                    return modpts,1 #'''
            #########################
            lon = temlon; lat = temlat
            #if i!=(t-1):                
            try:
                if self.modelname == "GOM3" or self.modelname == "30yr":
                    lonp,latp = self.nearest_point(lon, lat, lonl, latl,0.2)
                    #lonn,latn = self.nearest_point(lon,lat,lonk,latk,0.3)
                if self.modelname == "massbay":
                    lonp,latp = self.nearest_point(lon, lat, lonl, latl,0.03)
                    #lonn,latn = self.nearest_point(lon,lat,lonk,latk,0.05)
                index1 = np.where(self.lonc==lonp)
                index2 = np.where(self.latc==latp)
                elementindex = np.intersect1d(index1,index2); #print 'elementindex',elementindex
                #index3 = np.where(self.lons==lonn)
                #index4 = np.where(self.lats==latn)
                #nodeindex = np.intersect1d(index3,index4)
                
                ################## boundary 1 ####################
        
                pa = self.eline_path(lon,lat)
                ################## boundary 2 ####################
                '''if elementindex in b_index:
                    print 'boundary'
                    dss=math.sqrt((lonp-lonn)**2+(latp-latn)**2)
                    pa = Path.circle((lonp,latp),radius=dss)
                    if not pa.contains_point([lon,lat]):
                        print 'Sorry, point on the land here.Depends on Boundarypoint'
                        raise Exception()#
                else :
                    pa = self.boundary_path(lon,lat)#'''   
                ################## boundary 3 ####################
                '''if elementindex in b_index:
                    #if ([lonp,latp]==i).all():               
                    nod = nv[:,elementindex]; 
                    if not (nodeindex+1) in nod:
                        print 'Sorry, point on the land here.Depends on Boundarypoint'
                        raise Exception()#
                    else :
                        dss=math.sqrt((lonp-lonn)**2+(latp-latn)**2)
                        if distance>dss:               
                            print 'Sorry, point on the land here.Depends on Boundarypoint'
                            raise Exception()#'''                   
                #waterdepth = self.h[nodeindex]+zeta[i+1,nodeindex]
                '''if track_way=='backward' : # backwards case
                    waterdepth = self.h[nodeindex]+self.zeta[t-i-1,nodeindex]
                    modpts['time'].append(self.mTime[t-i-1])
                else:
                    waterdepth = self.h[nodeindex]+self.zeta[i+1,nodeindex]
                    modpts['time'].append(self.mTime[i+1])
                
                depth_total = self.siglay[:,nodeindex]*waterdepth  
                layer = np.argmin(abs(depth_total+depth)) #'''
                modpts['lon'].append(lon); modpts['lat'].append(lat);# modpts['layer'].append(layer); 
                print '%d,lat,lon,layer'%(i+1),temlat,temlon#layer
                '''if waterdepth<(abs(depth)): 
                    print 'This point hits the land here.Less than %d meter.'%abs(depth)
                    raise Exception()#'''
            except:
                return modpts,1
                                
        return modpts,2
        
class get_drifter(track):

    def __init__(self, drifter_id, filename=None):
        self.drifter_id = drifter_id
        self.filename = filename
    def get_track(self, starttime=None, days=None):
        '''
        return drifter nodes
        if starttime is given, return nodes started from starttime
        if both starttime and days are given, return nodes of the specific time period
        '''
        if self.filename:
            temp=getrawdrift(self.drifter_id,self.filename)
        else:
            temp=getdrift(self.drifter_id)
        nodes = {}
        nodes['lon'] = np.array(temp[1])
        nodes['lat'] = np.array(temp[0])
        nodes['time'] = np.array(temp[2])
        #starttime = np.array(temp[2][0])
        if not starttime:
            starttime = np.array(temp[2][0])
        if days:
            endtime = starttime + timedelta(days=days)
            i = self.__cmptime(starttime, nodes['time'])
            j = self.__cmptime(endtime, nodes['time'])
            nodes['lon'] = nodes['lon'][i:j+1]
            nodes['lat'] = nodes['lat'][i:j+1]
            nodes['time'] = nodes['time'][i:j+1]
        else:
            i = self.__cmptime(starttime, nodes['time'])
            nodes['lon'] = nodes['lon'][i:-1]
            nodes['lat'] = nodes['lat'][i:-1]
            nodes['time'] = nodes['time'][i:-1]
        return nodes
        
    def __cmptime(self, time, times):
        '''
        return indies of specific or nearest time in times.
        '''
        tdelta = []
        #print len(times)
        for t in times:
            tdelta.append(abs((time-t).total_seconds()))
            
        index = tdelta.index(min(tdelta))
        
        return index
class get_roms_rk4(get_roms):
    '''
    model roms using Runge Kutta
    '''
    def get_track(self, lon, lat, depth, url):
        '''
        get the nodes of specific time period
        lon, lat: start point
        url: get from get_url(starttime, endtime)
        depth: 0~35, the 36th is the bottom.
        '''
        self.startpoint = lon, lat
        
        if type(url) is str:
            nodes = self.__get_track(lon, lat, depth, url)
            
        else: # case where there are two urls, one for start and one for stop time
            nodes = dict(lon=[self.startpoint[0]],lat=[self.startpoint[1]])
            
            for i in url:
                temp = self.__get_track(nodes['lon'][-1], nodes['lat'][-1], depth, i)
                nodes['lon'].extend(temp['lon'][1:])
                nodes['lat'].extend(temp['lat'][1:])
                
        return nodes # dictionary of lat and lon
        
    def __get_track(self, lon, lat, depth, url):
        '''
        ???? ????
        '''
        data = self.get_data(url)
        nodes = dict(lon=lon, lat=lat)
        mask = data['mask_rho'][:]
        lon_rho = data['lon_rho'][:]
        lat_rho = data['lat_rho'][:]
        index, nearestdistance = self.nearest_point_index(lon,lat,lons,lats)
        depth_layers = data['h'][index[0][0]][index[0][1]]*data['s_rho']
        layer = np.argmin(abs(depth_layers+depth))
        u = data['u'][:,layer]
        v = data['v'][:,layer]
        
        for i in range(0, len(data['u'][:])):
            u_t = u[i, :-2, :]
            v_t = v[i, :, :-2]
            lon, lat, u_p, v_p = self.RungeKutta4_lonlat(lon,lat,lons,lats,u_t,v_t)
            
            if not u_p:
                print 'point hit the land'
                break
            nodes['lon'] = np.append(nodes['lon'],lon)
            nodes['lat'] = np.append(nodes['lat'],lat)
            
        return nodes
        
    def polygonal_barycentric_coordinates(self,xp,yp,xv,yv):
        '''
        ??? how is this one solved???
        '''
        N=len(xv)   
        j=np.arange(N)
        ja=(j+1)%N
        jb=(j-1)%N
        Ajab=np.cross(np.array([xv[ja]-xv[j],yv[ja]-yv[j]]).T,
                      np.array([xv[jb]-xv[j],yv[jb]-yv[j]]).T)
        Aj=np.cross(np.array([xv[j]-xp,yv[j]-yp]).T,
                    np.array([xv[ja]-xp,yv[ja]-yp]).T)
        Aj=abs(Aj)
        Ajab=abs(Ajab)
        Aj=Aj/max(abs(Aj))
        Ajab=Ajab/max(abs(Ajab))    
        w=xv*0.
        j2=np.arange(N-2)
        
        for j in range(N):
            
            w[j]=Ajab[j]*Aj[(j2+j+1)%N].prod()
          
        w=w/w.sum()
        
        return w
        
    def VelInterp_lonlat(self,lonp,latp,lons,lats,u,v):
        index, distance = self.nearest_point_index(lonp,latp,lons,lats)
        lonv,latv = lons[index[0],index[1]], lats[index[0],index[1]]
        w = self.polygonal_barycentric_coordinates(lonp,latp,lonv,latv)
        uf = (u[index[0],index[1]]/np.cos(lats[index[0],index[1]]*np.pi/180)*w).sum()
        vf = (v[index[0],index[1]]*w).sum()
        
        return uf, vf
        
    def RungeKutta4_lonlat(self,lon,lat,lons,lats,u,v):
        '''
        ?????????????
        '''
        tau = 60*60/111111.
        lon1=lon*1.;          lat1=lat*1.;        urc1,v1=self.VelInterp_lonlat(lon1,lat1,lons,lats,u,v);  
        lon2=lon+0.5*tau*urc1;lat2=lat+0.5*tau*v1;urc2,v2=self.VelInterp_lonlat(lon2,lat2,lons,lats,u,v);
        lon3=lon+0.5*tau*urc2;lat3=lat+0.5*tau*v2;urc3,v3=self.VelInterp_lonlat(lon3,lat3,lons,lats,u,v);
        lon4=lon+    tau*urc3;lat4=lat+    tau*v3;urc4,v4=self.VelInterp_lonlat(lon4,lat4,lons,lats,u,v);
        lon=lon+tau/6.*(urc1+2.*urc2+2.*urc3+urc4);
        lat=lat+tau/6.*(v1+2.*v2+2.*v3+v4); 
        uinterplation=  (urc1+2.*urc2+2.*urc3+urc4)/6    
        vinterplation= (v1+2.*v2+2.*v3+v4)/6
       
        return lon,lat,uinterplation,vinterplation

def min_data(*args):
    '''
    return the minimum of several lists
    '''
    data = []
    for i in range(len(args)):    
        data.append(min(args[i]))
    return min(data)
    
def max_data(*args):
    '''
    return the maximum of several lists
    '''
    data = []   
    for i in range(len(args)):
        data.append(max(args[i]))
    return max(data)
    
def angle_conversion(a):
    '''
    converts the angle into radians
    '''
    a = np.array(a)
    
    return a/180*np.pi
    
def dist(lon1, lat1, lon2, lat2):
    '''
    calculate the distance of points
    '''
    R = 6371.004
    lon1, lat1 = angle_conversion(lon1), angle_conversion(lat1)
    lon2, lat2 = angle_conversion(lon2), angle_conversion(lat2)
    l = R*np.arccos(np.cos(lat1)*np.cos(lat2)*np.cos(lon1-lon2)+
                    np.sin(lat1)*np.sin(lat2))
                    
    return l

    
def draw_basemap(ax, points, interval_lon=0.3, interval_lat=0.3):
    '''
    draw the basemap?
    '''
    
    lons = points['lons']
    lats = points['lats']
    size = max((max(lons)-min(lons)),(max(lats)-min(lats)))/1
    map_lon = [min(lons)-size,max(lons)+size]
    map_lat = [min(lats)-size,max(lats)+size]
    
    #ax = fig.sca(ax)
    dmap = Basemap(projection='cyl',
                   llcrnrlat=map_lat[0], llcrnrlon=map_lon[0],
                   urcrnrlat=map_lat[1], urcrnrlon=map_lon[1],
                   resolution='h',ax=ax)# resolution: c,l,i,h,f.
    dmap.drawparallels(np.arange(int(map_lat[0])-1,
                                 int(map_lat[1])+1,interval_lat),
                       labels=[1,0,0,0])
    dmap.drawmeridians(np.arange(int(map_lon[0])-1,
                                 int(map_lon[1])+1,interval_lon),
                       labels=[0,0,0,1])
    dmap.drawcoastlines()
    dmap.fillcontinents(color='grey')
    dmap.drawmapboundary()
    dmap.etopo()

def uniquecolors(N):
    """
    Generate unique RGB colors
    input: number of RGB tuples to generate
    output: list of RGB tuples
    """
    HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    colors =  [colorsys.hsv_to_rgb(x*1.0/N, 0.5, 0.5) for x in range(N)]
    return colors

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
    
def points_square(point, hside_length):
    '''point = (lat,lon); length: units is decimal degrees.
       return a squre points(lats,lons) on center point'''
    (lat,lon) = point; length =float(hside_length)
    lats=[lat]; lons=[lon]
    bbox = [lon-length, lon+length, lat-length, lat+length]
    bbox = np.array(bbox)
    points = np.array([bbox[[0,1,1,0]],bbox[[2,2,3,3]]])
    lats.extend(points[1]); lons.extend(points[0])
    
    return lats,lons

def extend_square(point, radius,num):
    '''point = (lat,lon); length: units is decimal degrees.
       return a squre points(lats,lons) on center point'''
    (lat,lon) = point; 
    lats=[lat]; lons=[lon]
    length =float(radius)/(num+1)
    for i in xrange(num+1):
        lth = length*(i+1)
        bbox = [lon,lon-lth,lon+lth,lat,lat-lth,lat+lth]
        bbox = np.array(bbox)
        points = np.array([bbox[[1,2,2,1,1,2,0,0]],bbox[[4,4,5,5,3,3,4,5]]])
        lats.extend(points[1]); lons.extend(points[0])

    return lats,lons
    
def extend_units(point, unit, num):
    '''point = (lat,lon); length: units is decimal degrees.
       return a squre points(lats,lons) on center point'''
    (lat,lon) = point; 
    lats=[]; lons=[]
    #unit = unit
    leh = unit*num
    
    #ps = np.mgrid[lat-leh:lat+leh+1:2j, lon-leh:lon+leh+1:2j]; print ps
    #ps = ps*unit
    lts = np.arange(lat-leh,lat+leh+unit,unit); lns = np.arange(lon-leh,lon+leh+unit,unit)
    llp = np.meshgrid(lts,lns); #print llp
    lats.extend(llp[0].flatten()); lons.extend(llp[1].flatten())

    return lats,lons

def totdis(lons,lats):
    "return path length of list points" 
    ts = 0
    lp = len(lons)-1
    for i in xrange(lp):
        dx = lons[i+1]-lons[i]
        dy = lats[i+1]-lats[i]
        ds = math.sqrt(dx**2+dy**2)
        ts += ds
    return ts
