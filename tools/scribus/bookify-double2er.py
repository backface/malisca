 #!/usr/bin/env python

from scribus import *
import os, time, datetime, math

######################################
imagepath = "/data/projects/slitscan/malisca/tile-data/2011-04-27--westautobahn-II/1440x320/"
#imagepath = "/data/projects/rivers-as-lines/satlisca/scan-data/nile/"
imagepath = "/data/projects/slitscan/malisca/tile-data/2011-12-13--varanasi-deshaked/2592x2592-bg_white"
imagepath = "/data/projects/slitscan/malisca/tile-data/2013-02-18--amazon-LNK"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2013-02-18--amazon/selection/128/"

#Lulu
page_size = (666,522) # lulu landscape inkl. anschnitt (6.3pt)
bleed = 6.3
orientation = LANDSCAPE # LANDSCAPE or PORTRAIT

#Lulu US Trade with bleed
page_size = (450,666) # lulu landscape inkl. anschnitt (6.3pt)
bleed = 6.3
orientation = PORTRAIT # LANDSCAPE or PORTRAIT

#Lulu quadrad with bleed
page_size = (558,558) # lulu landscape inkl. anschnitt (6.3pt)
bleed = 6.3
orientation = PORTRAIT # LANDSCAPE or PORTRAIT

#Blurb: Anschnitt 9pt, Rand: 18pt, Binderand:45pt
#page_size = (684,576) # blurb landscape ohne anschnitt (9pt)
#page_size = (693,594) # blurb landscape inkl anschnitt (9pt) - 
#bleed = 9
#orientation = LANDSCAPE # LANDSCAPE or PORTRAIT


#nt
page_size = (425.20,566.93)

tiles_per_row = 2
#tiles_per_row = 11
grid = False
margin_fac = 0.7
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

if orientation == "LANDSCAPE":
	page_w = page_size[1]
	page_h = page_size[0]
else:
	page_w = page_size[0]
	page_h = page_size[1]
	
tile_w = page_w / float(tiles_per_row)
tile_h = tile_w * 512 / 1000
tile_h = tile_w / 4
tile_h = tile_w

num_rows = math.floor(page_h / (tile_h + tile_h * margin_fac))
margin_h = (page_h - ( num_rows * tile_h + (num_rows-1) * tile_h * margin_fac )) / 2

progressTotal(len(D))
imagecount = 0
pagecount = 0
xpos = 0
ypos = margin_h
xkm = 0
ykm = 0
interval_km10  = tile_w / 2
count_km10 = 0
page2 = False

if not limit > 0:
	limit = len(D)

if len(D) > 0:
	if newDocument(page_size, (bleed,bleed,bleed,bleed), orientation, 1, UNIT_POINTS, FACINGPAGES, FIRSTPAGERIGHT, 1):
		newPage(-1)
		newPage(-1)
		gotoPage(currentPage()-1)
		
		while imagecount < limit:
			filename,ext = os.path.splitext(D[imagecount])
		
			if imagecount < limit:
				f = createImage(xpos, ypos, tile_w, tile_h)				
				loadImage(imagepath + "/" + D[imagecount], f)
				setScaleImageToFrame(scaletoframe=1, proportional=1, name=f)
				setLineStyle(0,f)
				imagecount = imagecount + 1				
			
				if grid:
					# make kilometer grid
					ykm = ypos + tile_h #+ 1
					#if xpos != 0:
					createLine(xpos, ykm , xpos, ykm + 2)
					createLine(xpos + tile_w/2, ykm , xpos + tile_w/2, ykm + 1.5)
					if xpos + tile_w < page_w:
						createLine(xpos + tile_w, ykm , xpos + tile_w, ykm + 1.5)
						if len(D) == imagecount:
							createLine(xpos + tile_w, ypos , xpos + tile_w, ypos + tile_h + 1)
							#text = "%d km " % (imagecount * 20)					
							#textname = "text%02d" % (imagecount)							
							#textfield = createText(xpos + tile_w + 2, ykm, 20, 5)
							#setFont("Blender Pro Book",textfield)
							#setTextAlignment(ALIGN_LEFT, textfield)
							#setFontSize(10, textfield)
							#setText(text,textfield)						
				
				
				xpos += tile_w
												
				if xpos >= page_w - 0.1:
					
					# make kilometer grid
					#ykm = ypos + tile_h + 1
					#km = xkm + interval_km10
					#while xkm <= page_w:					
					#	createLine(xkm, ykm , xkm, ykm + 2)
					#	xkm = xkm + (interval_km10)
					#	count_km10 += 1
					#	create kilometer text
					#	if count_km10 % 5 == 0:
					#		text = "%d km " % (count_km10 * 10)					
					#		textname = "text%02d" % (count_km10)							
					#		textfield = createText(xkm + 2, ykm + 2, 50, 10)
					#		#setFont("Blender Pro Book",textfield)
					#		setTextAlignment(1, textfield)
					#		setFontSize(6, textfield)
					#		setText(text,textfield)
					#		
					#xkm = xkm - page_w
						
					xpos = 0			
					if page2:
						ypos = ypos + tile_h + tile_h *margin_fac
						page2 = False
						gotoPage(currentPage()-1)

					else:
					   if math.floor(tiles_per_row) != tiles_per_row:
						   xpos = tile_w / 2
					   gotoPage(currentPage()+1)
					   page2 = True

				# new page
				if (imagecount < limit and ypos + tile_h >= page_h and not page2):
					if ypos + tile_h >= page_h:
						gotoPage(currentPage()+1)
						#text = "%d km " % (imagecount * 20)					
						#textname = "text%02d" % (imagecount)							
						#textfield = createText(page_w - 30, ypos - (tile_h *margin_fac)  + 1, 23.2, 5, textname)
						#setFont("Blender Pro Book",textfield)
						#setTextAlignment(ALIGN_RIGHT, textfield)
						#setFontSize(8, textfield)
						#setText(text,textfield)							
					newPage(-1)
					newPage(-1)
					gotoPage(currentPage()-1)
					ypos = margin_h
					xpos = 0
					page2 = False
								
			progressSet(imagecount)
			#redrawAll()
			#setRedraw(1)

	createLine(xkm, ykm , xkm, ykm + 2)

	
	setRedraw(1)
	redrawAll()

else:
	result = messageBox ('Not Found','No Images found with\n this search selection',BUTTON_OK)

