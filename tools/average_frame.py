#!/usr/bin/env python
#######################################
#
# convert movie to tiles or image strips
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

from PIL import ImageDraw, Image
import sys, os, subprocess
import getopt
import cv
from libs.slitscanner import SlitScanner
from libs.myutils import *
import numpy as np

output = "average.ppm"

format = "JPEG"
out_w = 2592
out_h = 2592
a = None
display = True
overwriteExisting = False
write_log_files = True
process_images = True
inputfiles = []
jp4 = False
scale=1.0
limit = 1000


def usage():
	print """
usage: average_frame.py -i MOVIEFILE -o OUTPUT [options]

convert movie file to images tiles or strips

options:
    -h, --help              print usage
    -i, --input=FILE        input movie file
    -o, --output=FILE       output path
        --jp4               jp4 mode
        --scale=VALUE       multiply input frame(s) by VALUE
        --limit=VALUE       limit to number of frames
"""

def process_args():
	global inputfile
	global output, limit
	global format, jp4,scale
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:f:",
			["help", "input=","output=","format=","jp4","scale=",
			"limit="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	for o, a in opts:
		if o == "-v":
			verbose = True
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-o", "--output"):
			output = a
		elif o in ("-i", "--input"):
			inputfile = a
		elif o in ("-f", "--format"):
			format = a
		elif o in ("--scale"):
			scale = float(a)
		elif o in ("--limit"):
			limit = int(a)			
		elif o in ("--jp4"):
			jp4 = True
		else:
			assert False, "unhandled option"

	if len(inputfile) == 0:
		print "inputfile required."
		usage()
		sys.exit(2)
		

if __name__ == '__main__':

	process_args()

	#open movie
	movie = cv.CaptureFromFile(inputfile)
	frame =  cv.QueryFrame(movie)

	black = Image.new("RGB", (frame.width,frame.height), (0,0,0))
	average = black.copy()

	nr = 0
	i = 0
	c = 0
	
	frame = cv.QueryFrame(movie)
	# read through movie max 100 frames
	while frame != None and nr < limit:
		if frame != None:
			nr+=1
			frame = cv.QueryFrame(movie)
	print "movies has %d frames!" % nr
	
	# now do it for real
	movie = cv.CaptureFromFile(inputfile)	
	frame =  cv.QueryFrame(movie)	
	while frame != None and i < limit:
		i+=1			
		if frame != None:
			if jp4:
				cv.SaveImage("tmp_frame.jpg",frame)
				subprocess.call(["elphel_dng","45","tmp_frame.jpg","tmp_frame.dng"])
				subprocess.call(["dcraw","-W","-q","3","tmp_frame.dng"])
				subprocess.call("rm tmp_frame.*",shell=True)
				img = Image.open("frame.ppm")
			else:
				img = Ipl2PIL(frame)
				img = swapRGB(img)

			im_frame = black.copy()
			im_frame.paste(img, (0,0))

			f = np.asarray(img)
			if a == None:
				a = np.asarray(black.copy())

			#a = (a+f*1.5)/2
			a = a + (f*scale)/(nr*(1.0))
			#a=a*(a < 255)+255*np.ones(np.shape(a))*(a > 255)
			# and blend this with our average 
			#alpha = 1.0/(nr)  # <-- clever part. Get average in constant memory.
                           # perhaps too clever. 
                           # images where most of the detail is just squished into one or two
                           # bits of depth. This may account for the slow darkening (?)
                           # may be better to combine images in a tree
			#average = Image.blend(average, im_frame, alpha)
			#
			average = Image.fromarray(a.astype('uint8'))
			
			average.save(output)			
						
			if display:
				average = swapRGB(average)
				cv_im =  PIL2Ipl(average)						
				
				cv.ShowImage("orig",frame)
				cv.ShowImage("preview",cv_im)
				cv.MoveWindow("preview",0, frame.height +24)
				
				if jp4:
					cv.ShowImage("frame",PIL2Ipl(img))
					cv.MoveWindow("frame",0,cv_im.height + (frame.height+24) + 24)

			cv.WaitKey(100)
		frame =  cv.QueryFrame(movie)
		
		print "processing frame %5d" % i
	cv.WaitKey(1000)

