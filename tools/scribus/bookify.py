 #!/usr/bin/env python

from scribus import *
import os, time, datetime, math

######################################
imagepath = "/data/projects/slitscan/malisca/tile-data/2011-12-16--chunar-banares/2592x2592"
offset = 0

#imagepath = "/data/projects/riverstudies/nile/tiles/2006-12-21-dv--edfu/"
#offset = 46

#imagepath = "/data/projects/slitscan/malisca/tile-data/2012-03-21--istanbul-straight/128"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-04-27--westautobahn-II/128x128"

imagepath = "/data/projects/slitscan/malisca/tile-data/2011-12-13--varanasi-LNK"
offset = 26

#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-12-13--varanasi/128"
#imagepath = "/data/projects/riverstudies/nile/tiles/2006-12-21-dv--edfu/"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2012-01-08--guwahati-north-deshaked/128"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-12-13--varanasi-east/128"

imagepath = "/data/projects/slitscan/malisca/tile-data/2011-06-17--linz-krems-LNK"


page_size = (666,522)
bleed = 6.3
page_size = (804,1417) # for EP
orientation = LANDSCAPE # LANDSCAPE or PORTRAIT
tiles_per_row = 13
margin_fac = 0.25 # 0.25
linewidth=0.7
limit = 10

###################################

filetype = []
dicttype = {'j':'.jpg','p':'.png','t':'.tif','g':'.gif','P':'.pdf','J':'.jpeg'}
Dicttype = {'j':'.JPG','p':'.PNG','t':'.TIF','g':'.GIF','P':'.PDF','J':'.JPEG'}
imagetype = "jJptgP"
#valueDialog('Image Types','Enter the Image Types, where\n j=jpg,J=jpeg,p=png,t=tif,g=gif,P=pdf\n "jJptgP" selects all','jJptgP')
for t in imagetype[0:]:
    filetype.append(dicttype[t])
    filetype.append(Dicttype[t])

D=[]
d = os.listdir(imagepath)
d.sort()
for file in d:
	for format in filetype:
		if file.endswith(format):
			D.append(file)
D.sort()

page_w = page_size[1]
page_h = page_size[0]
	
tile_w = page_w / float(tiles_per_row)
tile_h = tile_w
#tile_h = tile_w / 4

num_rows = math.floor(page_h / (tile_h + tile_h * margin_fac))
margin_h = (page_h - ( num_rows * tile_h + (num_rows-1) * tile_h * margin_fac )) / 2

progressTotal(len(D))
imagecount = offset
pagecount = 0
xpos = 0
ypos = margin_h

if not limit > 0:
	limit = len(D)

if len(D) > 0:
	if newDocument(page_size, (bleed,bleed,bleed,bleed), orientation, 1, UNIT_POINTS, FACINGPAGES, FIRSTPAGERIGHT, 1):
				
		while imagecount < limit:
			filename,ext = os.path.splitext(D[imagecount])
		
			if imagecount < limit:
				f = createImage(xpos, ypos, tile_w, tile_h)				
				loadImage(imagepath + "/" + D[imagecount], f)
				setScaleImageToFrame(scaletoframe=1, proportional=1, name=f)
				imagecount = imagecount + 1	
				
						
			
				xpos += tile_w
												
				if xpos >= page_w - 0.1:					
					xpos = 0
					ypos = ypos + tile_h + tile_h *margin_fac

				# new page
				if (imagecount < limit and ypos + tile_h >= page_h):					
					newPage(-1)
					ypos = margin_h
					xpos = 0
					
					

								
			progressSet(imagecount)
			#redrawAll()
			#setRedraw(1)


	
	setRedraw(1)
	redrawAll()

else:
	result = messageBox ('Not Found','No Images found with\n this search selection',BUTTON_OK)

