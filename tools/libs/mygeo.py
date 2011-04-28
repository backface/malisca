#!/usr/bin/env python
#######################################
#
# some geo helper functions
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

import math

R = 6371.2 * 1000 # earth radius in metres


# convert Degrees to Radian
def toRad(r):
	return r * math.pi/180

# convert Radian to Degrees
def toDeg(r):
	return r * 180.0 / math.pi
	

def getDistance(lat1, lon1, lat2, lon2):
	dLat = toRad(lat1 - lat2)
	dLon = toRad(lon1 - lon2)
	
	a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(toRad(lat1)) * math.cos(toRad(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = R * c

	return d


def getBearing( lat1,lon1,lat2,lon2):
	dLon = toRad(lon2 - lon1)
	
	y = math.sin(dLon) * math.cos(lat2)
	x = math.cos(toRad(lat1)) * math.sin(toRad(lat2)) - \
		math.sin(toRad(lat1)) * math.cos(toRad(lat2)) * math.cos(dLon)

	brng = toDeg(math.atan2(y, x))

	# return initial bearing
	return brng

def getBearingCompass(lat1, lon1, lat2, lon2):
	
	brng = getBearing(lat1, lon1, lat2, lon2)

	#normalize to compass readings (0-360)
	brng = (brng + 360) % 360

	return brng

def getMidPoint(lat1, lon1, lat2, lon2):
	dLon = toRad(lon1 - lon2)
	lat1 = toRad(lat1)
	lat2 = toRad(lat2)
	lon1 = toRad(lon1)
	 
	Bx = math.cos(lat2) * math.cos(dLon)
	By = math.cos(lat2) * math.sin(dLon)
	lat3 = math.atan2(math.sin(lat1)+math.sin(lat2),
           math.sqrt( (math.cos(lat1)+Bx)*(math.cos(lat1)+Bx) + By*By) )
	lon3 = lon1 + math.atan2(By, math.cos(lat1) + Bx)

	return toDeg(lat3), toDeg(lon3)

def getPointInDistance(lat, lon, brng, d):
	lat1 = toRad(lat)
	lon1 = toRad(lon)
	brng = toRad(brng)
	
	lat2 =  math.asin( math.sin(lat1) * math.cos(d/R)
			+ math.cos(lat1) * math.sin(d/R) * math.cos(brng) ) 
                      
	lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1), 
			math.cos(d/R)-math.sin(lat1)*math.sin(lat2)) 
			
	return (toDeg(lat2), toDeg(lon2))
     	


def getBearing_old( lat1,lon1,lat2,lon2):
	degreesPerRadian = 180.0 / math.pi
	
	# convert to Radians:
	lon1  =  lon1 * math.pi/180  
	lon2  =  lon2 * math.pi/180  
	lat1  =  lat1 * math.pi/180
	lat2  =  lat2 * math.pi/180

    # Compute the angle (old formula)
	#angle = math.atan2( math.sin(lon1 - lon2) * math.cos(lat2), math.cos(lat1) * math.sin(lat2) - math.sin(lat1) 
	#	* math.cos(lat2) * math.cos(lon1 - lon2) ) * (-1)

	dLon = lon2 - lon1
	
	y = math.sin(dLon) * math.cos(lat2)
	x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1) * \
		math.cos(lat2)*math.cos(dLon)

	brng = math.atan2(y, x) * 180.0 / math.pi
	brng = (brng+360) % 360

	return brng
                        
def getDistance_old(lat1,lon1,lat2,lon2):
	lon1  =  lon1 * math.pi/180  
	lon2  =  lon2 * math.pi/180  
	lat1  =  lat1 * math.pi/180
	lat2  =  lat2 * math.pi/180

	theta  = lon2 - lon1	

	# distance in meter		
	dist =  R * math.acos(
			math.sin(lat1) * math.sin(lat2) +
			math.cos(lat1) * math.cos(lat2) *
			math.cos(theta) )
	if dist:
		return dist
	else:
		return 0

def getDistGeod(lat1,lon1,lat2,lon2):
	from pyproj import Geod
	g = Geod(ellps='WGS84')
	az12, az21, dist = g.inv(lon1,lat1,lon2,lat2)
	return dist
