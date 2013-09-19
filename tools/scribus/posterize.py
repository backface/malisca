# -*- coding: utf-8 -*
#!/usr/bin/env python

from scribus import *
import os, time, datetime, math
import csv
#from pyproj import Geod

from config.config_poster_a1_walls_israel import Config

cfg = Config()

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
		
	
if cfg.readLogs:
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
files = os.listdir(cfg.imagepath)

images=[]
for file in files:
	for format in filetype:
		if file.endswith(format):
			images.append(file)
images.sort()

imagenum = len(images) - cfg.offset

limit = cfg.limit
offset = cfg.offset

if limit > 0:
	imagenum = limit - cfg.offset
	
if limit > imagenum:
	limit = imagenum

yscale = 0.2
if cfg.orientation == LANDSCAPE:
	page_w = cfg.page_size[1]
	page_h = cfg.page_size[0]
else:
	page_w = cfg.page_size[0]
	page_h = cfg.page_size[1]

page_ratio = page_h / page_w
page_area = page_w * page_h
page_area_margins = page_w * (page_h * cfg.margin_fac)
#length_total = len(images) * 

tile_w = math.sqrt( (page_area - page_area_margins) / imagenum )
tile_w = page_w / (math.floor(page_w / tile_w))
tile_h = tile_w
#tile_h = tile_w * 320 / 1440

num_columns = page_w / tile_w
num_rows = imagenum / num_columns

if limit == 0:
	limit = num_columns * math.floor(num_rows)
num_rows = math.floor(num_rows)
margin_h = (page_h - (num_rows * tile_h + num_rows * tile_h * cfg.margin_fac )) / 2 

print tile_w, num_columns, num_rows
print num_columns * num_rows
print "limit:", limit

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
	if newDocument(cfg.page_size, (cfg.margin,cfg.margin,cfg.margin,cfg.margin), cfg.orientation, 1, cfg.units, NOFACINGPAGES, 0, 1):
		
		while imagecount < limit:
			filename,ext = os.path.splitext(images[imagecount])
		
			if imagecount < limit:
				f = createImage(xpos, ypos, tile_w, tile_h)				
				loadImage(cfg.imagepath + "/" + images[imagecount + cfg.offset], f)
				setScaleImageToFrame(scaletoframe=1, proportional=1, name=f)
				setLineStyle(0,f)					
				xpos += tile_w
				
				if xpos + 0.1 >= page_w:	
					xpos = 0
					ypos = ypos + tile_h + tile_h * cfg.margin_fac

				if cfg.readLogs:
					logfile = cfg.imagepath + "/" + filename + ".log"
					if not os.path.exists(logfile):
						logfile = cfg.imagepath + "/" + images[imagecount+offset] + ".log"
					if os.path.exists(logfile):
						
						if cfg.logstyle == "old":							
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

		if cfg.readLogs:
			text = "%s  ·  %0.4f° %0.4f° - %0.4f° %0.4f°  ·  TIME [UTC]: %s - %s  ·  DISTANCE: %0.2f km  ·  %s"  % (cfg.title, firstPos[0], firstPos[1], lastPos[0], lastPos[1], firstPos[2], lastPos[2],
			(distance / 1000), cfg.footer)
		else:
			text = "%s  ·  %s" % (cfg.title, cfg.footer)
							
		textname = "info"
		#textfield = createText(margin, page_h - (2 * margin) - 12, page_w- 2*margin, 12, textname)
		th = 16
		textfield = createText(cfg.margin, margin_h + num_rows*(tile_w+tile_w* cfg.margin_fac),
			page_w- 3 * cfg.margin, th, textname)
		setFont("Catalog Regular", textfield)
		setTextAlignment(ALIGN_RIGHT, textfield)
		setFontSize(8, textfield)
		setTextColor("Grey30",textfield)
		setText(text,textfield)


	setRedraw(1)
	redrawAll()

else:
	result = messageBox ('Not Found','No Images found with\n this search selection',BUTTON_OK)





