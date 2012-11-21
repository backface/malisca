 #!/usr/bin/env python

from scribus import *
import os, time, datetime, math

######################################
imagepath = "/data/projects/slitscan/malisca/tile-data/2011-12-16--chunar-banares/2592x2592"
imagepath = "/data/projects/slitscan/malisca/tile-data/2011-06-17--linz-krems/2592x1296/"
page_size = PAPER_A4
#page_size = (209.9,297.0) #A4
#page_size = (216.2,303.3) #A4 + Lulu bleed
bleed = 6.3
orientation = LANDSCAPE # LANDSCAPE or PORTRAIT
tiles_per_row = 5
margin_fac = 0.25
linewidth=0.7
limit = 0
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
tile_h = tile_w * 512 / 1000
#tile_h = tile_w

num_rows = math.floor(page_h / (tile_h + tile_h * margin_fac))
margin_h = (page_h - ( num_rows * tile_h + (num_rows-1) * tile_h * margin_fac )) / 2

progressTotal(len(D))
imagecount = 400
pagecount = 0
xpos = 0
ypos = margin_h

if not limit > 0:
	limit = len(D)

if len(D) > 0:
	#if newDocument(page_size, (bleed,bleed,bleed,bleed), orientation, 1, UNIT_MILLIMETERS, FACINGPAGES, FIRSTPAGERIGHT, 1):
	if newDocument(page_size, (bleed,bleed,bleed,bleed), orientation, 1, UNIT_POINTS, NOFACINGPAGES, 0, 1):
				
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

