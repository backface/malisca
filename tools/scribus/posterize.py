# -*- coding: utf-8 -*
#!/usr/bin/env python

from scribus import *
import os, time, datetime, math
import csv
#from pyproj import Geod

######################################
#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-04-18--krems-linz/128x128"
#imagepath = "/home/mash/data/projects/rivers-as-lines/satlisca/scan-data/ganges/20.0m/12/landsat/512"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-06-17--linz-krems/512x512"
#imagepath = "/data/projects/rivers-as-lines/satlisca/scan-data/nile-via-damietta/20m/12/landsat/512/"
#imagepath = "/data/projects/rivers-as-lines/satlisca/scan-data/danube-via-sulina+breg/20m/12/landsat/512/"
#imagepath = "/data/projects/donau//scan-data/2006-04-17--pwc-asten-wien/"
#imagepath = "/data/projects/donau//scan-data/2005-07-23--pwc-almasfuszito-hainburg/"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-04-27--westautobahn-Ib/320x320/"
#imagepath = "/data/projects/slitscan/old/pd-slitscanner/scan-data/2011-04-18--krems-linz/"

imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-13--varanasi-deshaked/2592x2592-bg_white"
offset = 7
limit = 117
readLogs = True
logstyle = "new"
page_size = PAPER_A2
orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
footer = "Copyright © Michael Aschauer, 2011"
title = "A CHEAP LOW-QUALITY SAMPLE: Along The Ghats of Varanasi/Banaras - The Forest of Bliss"

# VARANASI recording
#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi-deshaked/2592x2592-level/"
#offset = 34
#limit = 177
#readLogs = False
#page_size = PAPER_A1
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#footer = "Copyright © Michael Aschauer, http://m.ash.to, 2011"
#title = "Along The Ghats of Benaras - The Forest of Bliss"

# EASTERN SIDE
#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi/2592x2592/"
#offset = 224
#limit = 0
#readLogs = False
#page_size = PAPER_A2
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#footer = "Copyright © Michael Aschauer, 2011"

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi-deshaked/2536x2536/"
#offset = 224
#limit = 0
#readLogs = False
#page_size = PAPER_A2
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#footer = "Copyright © Michael Aschauer, 2011"

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi/2592x2592/"
#offset = 25
#limit = 178

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-15--banares-chunar/128/"
#offset = 37
#limit = 0

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-16--chunar-banares/128/"
#offset = 0
#limit = 0



#footer = "Danube Panorama Project - http://danubepanorama.net  ·  Copyright © Michael Aschauer, 2011"
#footer = "Copyright © Michael Aschauer, 2011"
#footer = ""

#title = "Komarom (HU) - Hainburg (AT)"
#title = "Weissenkirchen (AT) - Linz (AT)"
#title = "Linz (AT) - Krems (AT)"
#title = "WHAT IF YOU WOULD PULL NILE TO A STRAIGHT LINE?  ·  The Nile from its tributaries Nyabarong and  Kagera (Rwanda) to the Mediterrian Sea via the Damietta branch"
#title = "WHAT IF YOU WOULD PULL GANGES TO A STRAIGHT LINE?"
#title = ""

#page_size = PAPER_A2
units = UNIT_POINTS
orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
margin = 14.2

#page_size = (600,900)
#units = UNIT_MILLIMETERS
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#margin = 5

margin_fac = 0.33




###################################

R = 6371.2 * 1000 # earth radius in metres
def getDistance(lat1, lon1, lat2, lon2):
	dLat = toRad(lat1 - lat2)
	dLon = toRad(lon1 - lon2)
	
	a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(toRad(lat1)) * math.cos(toRad(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = R * c

	return d

# convert Degrees to Radian
def toRad(r):
	return r * math.pi/180

# convert Radian to Degrees
def toDeg(r):
	return r * 180.0 / math.pi
		
	
if readLogs:

	#g = Geod(ellps='WGS84')
	distance = 0
	hasFirst = False

filetype = []
dicttype = {'j':'.jpg','p':'.png','t':'.tif','g':'.gif','P':'.pdf','J':'.jpeg'}
Dicttype = {'j':'.JPG','p':'.PNG','t':'.TIF','g':'.GIF','P':'.PDF','J':'.JPEG'}
imagetype = "jJptgP"
#valueDialog('Image Types','Enter the Image Types, where\n j=jpg,J=jpeg,p=png,t=tif,g=gif,P=pdf\n "jJptgP" selects all','jJptgP')
for t in imagetype[0:]:
    filetype.append(dicttype[t])
    filetype.append(Dicttype[t])

files=[]
files = os.listdir(imagepath)

images=[]
for file in files:
	for format in filetype:
		if file.endswith(format):
			images.append(file)
images.sort()

imagenum = len(images) - offset

if limit > 0:
	imagenum = limit - offset
	
if limit > imagenum:
	limit = imagenum


yscale = 0.8
if orientation == LANDSCAPE:
	page_w = page_size[1]
	page_h = page_size[0]
else:
	page_w = page_size[0]
	page_h = page_size[1]

page_ratio = page_h / page_w
page_area = page_w * page_h
page_area_margins = page_w * (page_h * margin_fac)
#length_total = len(images) * 

tile_w = math.sqrt( (page_area - page_area_margins) / imagenum )
tile_w = page_w / (math.floor(page_w / tile_w))
tile_h = tile_w

num_columns = page_w / tile_w
num_rows = imagenum / num_columns

if limit == 0:
	limit = num_columns * math.floor(num_rows)
num_rows = math.floor(num_rows)
margin_h = (page_h - (num_rows * tile_h + num_rows * tile_h * margin_fac )) / 2 

print tile_w, num_columns, num_rows
print num_columns * num_rows
print limit

progressTotal(imagenum)
imagecount = 0
pagecount = 0
xpos = 0
ypos = margin_h
xkm = 0
ykm = 0
hasFirst = False


if not limit > 0:
	limit = imagenum

if imagenum > 0:
	if newDocument(page_size, (margin,margin,margin,margin), orientation, 1, units, NOFACINGPAGES, 0, 1):
		
		while imagecount < limit:
			filename,ext = os.path.splitext(images[imagecount])
		
			if imagecount < limit:
				f = createImage(xpos, ypos, tile_w, tile_h)				
				loadImage(imagepath + "/" + images[imagecount+offset], f)
				setScaleImageToFrame(scaletoframe=1, proportional=0, name=f)
				setLineStyle(0.0,f)					
				xpos += tile_w
				
				if xpos + 0.1 >= page_w:	
					xpos = 0
					ypos = ypos + tile_h + tile_h *margin_fac

				if readLogs:
					logfile = imagepath + "/" + filename + ".log"
					if not os.path.exists(logfile):
						logfile = imagepath + "/" + images[imagecount+offset] + ".log"
					if os.path.exists(logfile):
						
						if logstyle == "old":							
							logreader = csv.reader(open(logfile,"rb"), delimiter=" ")
							for pos in logreader:
								if not pos[0] == ";": #temp hack
									lastPos = (float(pos[2]),float(pos[3]),pos[1].strip())
									if not hasFirst:
										firstPos = (float(pos[2]),float(pos[3]),pos[1].strip())
										prevPos = (float(pos[2]),float(pos[3]),pos[1].strip())
										hasFirst = True
									else:
										#az12, az21, dist = g.inv(prevPos[1],prevPos[0],lastPos[1],lastPos[0])
										#distance +=	dist
										distance += getDistance(prevPos[0],prevPos[1],lastPos[0],lastPos[1])
										prevPos = (float(pos[2]),float(pos[3]),pos[4].strip())
						else:
							logreader = csv.reader(open(logfile,"rb"), delimiter=";")
							try:
								for pos in logreader:
									lastPos = (float(pos[3]),float(pos[4]),pos[1].strip())
									if not hasFirst:
										firstPos = (float(pos[3]),float(pos[4]),pos[1].strip())
										prevPos = (float(pos[3]),float(pos[4]),pos[1].strip())
										hasFirst = True
									else:
										#az12, az21, dist = g.inv(prevPos[1],prevPos[0],lastPos[1],lastPos[0])
										#distance +=	dist
										distance += getDistance(prevPos[0],prevPos[1],lastPos[0],lastPos[1])
										prevPos = (float(pos[3]),float(pos[4]),pos[1].strip())
							except:
								# print help information and exit:
								#print str(err) # will print something like "option -a not recognized"
								print "error reading log file:", logfile
					else:
						print "file not found:", logfile

				imagecount = imagecount + 1
					
				if (imagecount < limit and ypos + tile_h >= page_h):
					newPage(-1)
					ypos = margin_h
					xpos = 0			
					
			progressSet(imagecount-offset)
			redrawAll()

		if readLogs:
			text = "%s  ·  %0.4f° %0.4f° - %0.4f° %0.4f°  ·  TIME [UTC]: %s - %s  ·  DISTANCE: %0.2f km  ·  %s" %  (title, firstPos[0], firstPos[1], lastPos[0], lastPos[1], firstPos[2], lastPos[2],
			(distance / 1000), footer)
		else:
			text = "%s  ·  %s" % (title, footer)
							
		textname = "info"
		#textfield = createText(margin, page_h - (2 * margin) - 12, page_w- 2*margin, 12, textname)
		th = 12
		textfield = createText(margin, margin_h + num_rows*(tile_w+tile_w*margin_fac)-th,
			page_w- 3*margin, th, textname)
		setFont("Catalog Pro Regular",textfield)
		setTextAlignment(ALIGN_RIGHT, textfield)
		setFontSize(8, textfield)
		setTextColor("Grey30",textfield)
		setText(text,textfield)


	setRedraw(1)
	redrawAll()

else:
	result = messageBox ('Not Found','No Images found with\n this search selection',BUTTON_OK)





