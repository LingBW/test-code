    def boundary_path(self,lon,lat):
        p = Path.circle((lon,lat),radius=0.03)
        dis = []
        for i in self.b_points:
            if p.contains_point(i):
                d = math.sqrt((lon-i[0])**2+(lat-i[1])**2)
                dis.append(d)
        if dis:
            md = min(dis)
            pa = Path.circle((lon,lat),radius=md+0.005)
            return pa
        else: return None
    
    def line_path(self,lon,lat):
        p = Path.circle((lon,lat),radius=0.028)
        dis = []; bps = []
        for i in self.b_points:
            if p.contains_point(i):
                bps.append((i[0],i[1]))
                d = math.sqrt((lon-i[0])**2+(lat-i[1])**2)
                dis.append(d)
        print 'length',len(dis)
        if len(dis)<3 :
            return None
        else:
            dnp = np.array(dis)
            dis.sort()
            dis0 = dis[0]; dis1 = dis[1]; dis2 = dis[2]
            p0 = np.where(dnp==dis0);p1 = np.where(dnp==dis1); p2 = np.where(dnp==dis2)
            #print '00000',p0[0],p1
            bps0 = bps[p0[0]]; bps1 = bps[p1[0]]; bps2 = bps[p2[0]]
            pa = [bps1,bps0,bps2]; #print 'pa',pa
            #codes = [Path.MOVETO,Path.LINETO,Path.LINETO]
            path = Path(pa)#,codes
            return path
        
    def eline_path_old(self,lon,lat):
        '''
        When drifter close to boundary(less than 0.1),find one nearest point to drifter from boundary points, 
        then find two nearest boundary points to previous boundary point, create a boundary path using that 
        three boundary points.
        '''
        p = Path.circle((lon,lat),radius=0.1) #0.06
        dis = []; bps = []
        for i in self.b_points:
            if p.contains_point(i):
                bps.append((i[0],i[1]))
                d = math.sqrt((lon-i[0])**2+(lat-i[1])**2)
                dis.append(d)
        if len(dis)<3 :
            return None
        dnp = np.array(dis)
        dis.sort()
        if dis[0]>0.05 :
            return None
        
        else :
            cdis = []; cbps = []
            dis0 = dis[0]
            p = np.where(dnp==dis0)   
            bps0 = bps[p[0]]
            p1 = Path.circle(bps0,radius=0.04)
            for j in bps:
                if p1.contains_point(j):
                    cbps.append((j[0],j[1]))
                    d1 = math.sqrt((lon-j[0])**2+(lat-j[1])**2)
                    cdis.append(d1)
            if len(cdis)<3 :
                return None
            dnp1 = np.array(cdis)
            cdis.sort()            
            cdis1 = cdis[1]; cdis2 = cdis[2]
            p1 = np.where(dnp1==cdis1); p2 = np.where(dnp1==cdis2)
            bps1 = cbps[p1[0]]; bps2 = cbps[p2[0]]
            pa = [bps1,bps0,bps2]; #print 'pa',pa
            #codes = [Path.MOVETO,Path.LINETO,Path.LINETO]
            path = Path(pa)#,codes
            return path
    
    def eline_path2(self,lon,lat):
        '''
        When drifter close to boundary(less than 0.1),find one nearest point to drifter from boundary points, 
        then find two nearest boundary points to previous boundary point, create a boundary path using that 
        three boundary points.
        '''
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
            elementindex = np.intersect1d(index1,index2) # location 753'''
            print index1,index2,elementindex  
            dx = self.pointt[elementindex]; #print dx 
            for i in dx[0]: # i is a number.
                #print i  
                if i ==0 :
                    continue
                dx1 = self.pointt[i-1]; #print dx1
                if 0 in dx1:
                    loca.append(i-1)
                else:
                    for j in dx1:
                        if j != elementindex[0]+1:
                            if self.wl[j-1] == 1:
                                loca.append(j-1)
                            
            for i in loca:
                tlons.append(self.lonc[i]); tlats.append(self.latc[i])
            tlons.insert(1,lonp); tlats.insert(1,latp)            
            for i in xrange(len(tlons)):
                pa.append((tlons[i],tlats[i]))
            path = Path(pa)#,codes
            return path
