# -*- coding: utf-8 -*-
#!/usr/bin/env python
#######################################
#
# GPXwriter and Infowriter classes
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################



from mygeo import *

class GPXWriter:

	def __init__(self, filename):		
		self.lastUTC = ""
		self.filename = filename
		self.content = self.getHeader()

	def open(self,filename):
		self.filename = filename
		self.content = self.getHeader()
		self.lastUTC = ""			
		
	def save(self):
		self.fh = open(self.filename,"wb")
		self.fh.write(self.content)
		self.fh.write(self.getFooter())
		self.close()	
				
	def close(self):
		self.fh.close()

	def writeHeader(self):
		self.fh.write(self.getHeader())

	def writeFooter(self):
		self.fh.write(self.getHeader())	
		
	def addTrackpoint(self,lat=0,lon=0,utc="",ele=-1000,speed=-1000,fix=-1,name="",cmt=""):
		if utc and utc!=self.lastUTC:
			self.content += '      <trkpt lat="%f" lon="%f">\n' % (lat,lon)
			if ele > -1000:
				self.content += '        <ele>%f</ele>\n' % ele
			if speed > -1000:
				self.content += '        <speed>%f</speed>\n' % speed
			if utc:
				self.content += '        <time>%s</time>\n' % utc.strip()
			if name != "":
				self.content += '        <name>%s</name>\n' % name				
			if cmt != "":
				self.content += '        <cmt>%s</cmt>\n' % cmt	
			if fix.strip() > 0:
				if fix.strip() == "3":
					fix = "3d"
				elif fix.strip() == "2":
					fix = "2d"
				self.content += '        <fix>%s</fix>\n' % fix.strip()			
			self.content += '      </trkpt>\n'
		self.lastUTC = utc

	def getHeader(self):
		header = "<?xml version='1.0' encoding='UTF-8'?>\n"
		header += '''<gpx version="1.1" creator="JOSM GPX export" xmlns="http://www.topografix.com/GPX/1/1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">\n'''
		header += "  <trk>\n"
		header += "    <trkseg>\n"
		return header

	def getFooter(self):
		footer = '    </trkseg>\n'
		footer += '  </trk>\n'
		footer += '</gpx>'
		return footer	

class GeoInfoWriter():

	def __init__(self, filename):
		self.dist = 0
		self.first_point = (100,100)
		self.last_point = (100,100)
		self.hasFirst = False
		self.prevLat = 0
		self.prevLon = 0
		self.lastTime = ""
		self.firstTime = ""
		self.name = ""
		self.filename = filename

	def reset(self):
		self.dist = 0
		self.hasFirst = False
		
	def open(self,filename):
		self.filename = filename		
		self.dist = 0
		self.hasFirst = False

	def save(self):
		self.fh = open(self.filename,"wb")
		self.fh.write(self.getInfoString())
		self.fh.close()

	def addPoint(self,lat=0,lon=0,utc="",ele=-1000,speed=-1000,hdop=-1,name=""):
		if not self.hasFirst:
			self.first_point = (lat,lon)
			self.firstTime = utc
			self.hasFirst = True
		else:
			self.dist += getDistGeod(
				self.prevLat, self.prevLon,
				lat, lon)

		self.prevLat = lat
		self.prevLon = lon
		self.name = name
		self.lastTime = utc
		self.last_point = (lat,lon)

	def getInfoString(self):
		info = "From: %f° %f° to: %f° %f°\n" % \
			(self.first_point[0], self.first_point[1],
			 self.last_point[0], self.last_point[1])
		info += "Time: %s to %s\n" % \
			(self.firstTime, self.lastTime)
		info += "Distance: %0.3fkm\n" % (self.dist / 1000)
		return info

	def getInfoStringHTML(self):
		info = "FROM: %f° %f° TO: %f° %f°<br />\n" % \
			(self.first_point[0], self.first_point[1],
			 self.last_point[0], self.last_point[1])
		info += "TIME: %s to %s<br />\n" % \
			(self.firstTime, self.lastTime)
		info += "DISTANCE: %0.3fkm<br />\n" % (self.dist / 1000)
		return info

	def getDist(self):
		return self.dist
