#!/usr/bin/env python
#######################################
#
# convert movie frames to tiles or image strips
# optionaly process gps (csv) log files
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

from PIL import ImageDraw, Image, ImageChops, ImageOps
import sys, os, subprocess, shlex
import getopt
import cv
import csv
import glob, re
import numpy as np
from libs.slitscanner import SlitScanner
from libs.gpxwriter import GPXWriter, GeoInfoWriter
from libs.myutils import *

output = "tile-data"
format = "JPEG"
out_w = 2592
out_h = 2592
scale = 1
display = True
overwriteExisting = False
write_log_files = True
process_images = True
inputfiles = []
darkframe = ""
whiteframe = ""
flag_calibration = False
reverse = False
jp4 = False
jp4_gamma = 45
crop=0
stretch = 1
gamma = -1
dist = 0
verbose = True
prefix = ""
isFull = False
lastUTC = ""
hadfirst = False
offset = 0

def usage():
	print """
usage: movie2tiles.py -i MOVIEFILE [-i FILE.gpx ..] [options]

convert movie file to images tiles or strips

options:
    -h, --help              print usage
    -i, --input=FILE        input movie file
    -o, --output=PATH       output path
    -x, --width=WIDTH       width of output tiles
    -y, --height=HEIGHT     height if output tiles
    -s, --size=WIDTHxHEIGHT final image size
    -n, --nodisplay         don't display visual output
        --gamma             apply gamma 
        --darkframe=FILE    darkframe
        --whiteframe=FILE   white (or grey) frame
        --calibration       apply darkframe substraction and whiteframe
                            division
        --reverse           flip image and reverse sequence
        --jp4               jp4 input
        --jp4-gamma	        gamma value for jp4 conversion
    -c, --crop=PIXELS       crop pixels
        --stretch=RATIO	    strech images
    -f, --format=FORMAT     image format for cache and output
                             [JPEG,PNG,TIFF] - default: JPEG
        --nologs            don't write gps-logfiles for scanned img
        --logsonly          just write gps-logfiles for scanned img
        --nodisplay         don't display
        --verbose           be verbose
        --prefix=NAME       set PREFIX for filename
"""

def process_args():
	global inputfiles
	global output, overwriteExisting, verbose, prefix
	global display, format, out_w, out_h, crop, stretch, gamma
	global process_images, write_log_files, jp4, jp4_gamma
	global darkframe, whiteframe, flag_calibration, reverse
	global offset
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:n:s:z:l:x:y:m:wf:c:g",
			["help", "input=","output=","overwrite","nodisplay","format=",
			"nologs","logsonly","darkframe=","whiteframe=","calibration",
			"reverse","jp4","jp4-gamma=","crop=","stretch=", "size=","offset=",
			"gamma=","verbose","prefix="])
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
			flist = a.split(" ")
			for f in flist:				
				if len(glob.glob(f)) > 1:
					f = glob.glob(f)
					f.sort();
					for ff in f:
						inputfiles.append(ff)
				else:
					inputfiles.append(f)		
		elif o in ("-y", "--height"):
			size = (size[0],a)
		elif o in ("-n", "--name"):
			name = a
		elif o in ("-f", "--format"):
			format = a
		elif o in ("-s", "--size"):
			a = a.split("x")
			out_w = int(a[0])
			out_h = int(a[1])						
		elif o in ("-w","--overwrite"):
			overwriteExisting = True
		elif o in ("--calibration"):
			flag_calibration = True
		elif o in ("--verbose"):
			verbose = True			
		elif o in ("--darkframe"):
			darkframe = a			
		elif o in ("--whiteframe"):
			whiteframe = a		
		elif o in ("--nodisplay"):
			display = False
		elif o in ("--nologs"):
			write_log_files = False
		elif o in ("--reverse"):
			reverse = True			
		elif o in ("--jp4"):
			jp4 = True
		elif o in ("--jp4-gamma"):
			jp4_gamma = a
		elif o in ("--gamma"):
			gamma = float(a)
		elif o in ("c","--crop"):
			crop = int(a)
		elif o in ("--stretch"):
			stretch = float(a)			
		elif o in ("--prefix"):
			prefix = a
		elif o in ("--offset"):
			offset = int(a)
		elif o in ("--logsonly"):
			write_log_files = True
			process_images = False
			display = False
		else:
			assert False, "unhandled option"

	if len(inputfiles) == 0:
		print "inputfile required."
		usage()
		sys.exit(2)
		

if __name__ == '__main__':
	process_args()

	if display:
		# deternamine screen size
		p = subprocess.Popen("xrandr | grep '*'",shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
		screen = shlex.split(p.stdout.read())[0].split("x")

	# init slitscanner
	slitscanner = SlitScanner()
	slitscanner.setFileType("JPEG")
	slitscanner.setPath(output + "/")
	slitscanner.setSize(out_w,out_h)

	if flag_calibration:
		if darkframe:
			df_im = Image.open(darkframe)
			df = np.asarray(df_im)
						
		# apply gamma to gray frame
		#gf_gamma = 0.89
		#gf_im = imageGamma(gf_im, (gf_gamma,gf_gamma,gf_gamma))
						
		#normalize whiteframe
		#gf_im.load()
		#gf_im = normalizeImage(gf_im)
		#gf_im.load()
		#gf_im2 = gf_im.copy()
		#gf_im2 = normalizeImage(gf_im2)

		if whiteframe:
			gf_im = Image.open(whiteframe)	
			b = np.asarray(gf_im)
			if darkframe:
				b = b - df			
			b2 = b
			#b = b/(b.max()./255.0)
			b = (b)/((b.max().astype("float")+1)/256.0)
			b=b*(b < 255)+255*np.ones(np.shape(b))*(b > 255)		
			b2 = (b2-b2.min())/((b2.max()-b2.min())/255.0)						
			gf_im_n = Image.fromarray(b.astype('uint8'))
			gf_im_n2 = Image.fromarray(b2.astype('uint8'))

			#apply gamma to grey frame
			#b = np.asarray(imageGamma(Image.fromarray(b.astype('uint8')),
			# (gf_gamma,gf_gamma,gf_gamma)))		

	if reverse:
		slitscanner.setReverse(True)

	if prefix:	
		slitscanner.setFilePrefix(prefix)

		
	gpxalltrackwriter = GPXWriter(slitscanner.getFileDirectory() +
		slitscanner.getFilePrefix() + ".gpx")
	infoallwriter = GeoInfoWriter(slitscanner.getFileDirectory() +
		slitscanner.getFilePrefix() + ".info")			

	totalframecount = 0
	slitcount = 0
	px_pos = 0
	imgcount = 0

	#print glob(inputfiles);
	
	
	for moviefile in inputfiles:
		
		movie = cv.CaptureFromFile(moviefile)
		frame =  cv.QueryFrame(movie)
		framecount = 0

		if not prefix:
			slitscanner.setFilePrefix(os.path.basename(moviefile).split(".")[0])

		if not hadfirst:
			ratio = out_h / float(frame.width)
			lh = int((frame.height-crop) * ratio * stretch)
			slitscanner.setSlitWidth(lh)		
			framecount = 0
			line = [0,0]
			hadfirst = True
		
		# open and init log files
		if write_log_files:
			logfile = moviefile + ".log"
			if jp4:
				if not os.path.exists(logfile):
					logfile = moviefile[:-8] + ".avi.log"
					
			logreader = csv.reader(open(logfile,"rb"), delimiter=";")
			
			noMoreLogLine = False
			line = logreader.next()
			if line[0].find("#"):
				line = logreader.next()
			
			createPath(slitscanner.getFileName() + ".log")
			logwriter = csv.writer(open(slitscanner.getFileName() + ".log","wb"),
					delimiter=";")
			infowriter = GeoInfoWriter(slitscanner.getFileName() + ".info")			
			gpxwriter = GPXWriter(slitscanner.getFileName() + ".gpx")			
			
		# main loop
		while frame != None:
			
			if frame != None:

				px_pos = (imgcount  * out_w ) + (framecount * lh)
				if reverse:
					px_pos *= -1

				print px_pos, offset, imgcount, slitcount
								
				if offset <= px_pos:
					if (not overwriteExisting  and slitscanner.fileExists()):
						# add frame - if full save logs
						isFull = slitscanner.addButDontScanFrame()
						if verbose:
							print "EXISTS frame #%05d (%s) to file: %s" % \
							 (totalframecount, moviefile, slitscanner.getFileName())							
					else:
						#jp4 mode pre-processing
						if jp4:
							cv.SaveImage("tmp_frame.jpg",frame)
							subprocess.call("elphel_dng %d tmp_frame.jpg tmp_frame.dng" % jp4_gamma,shell=True)
							subprocess.call(["dcraw","-W","-q","3", "tmp_frame.dng"])
							img_frame = Image.open("tmp_frame.ppm")
							subprocess.call("rm tmp_frame*", shell=True)						
						else:
							img_frame = Ipl2PIL(frame)
							img_frame = swapRGB(img_frame)
						pi = img_frame

							
						# first tests in pattern noise elimination
						if flag_calibration:
							
							#substract darkframe
							#pi = ImageChops.subtract(pi,df_im)
							#pi_dfsub = substractImage(pi,df_im)

							if whiteframe:
								a = np.asarray(pi)
								
							if darkframe:
								a = a-df
								pi_dfsub = Image.fromarray(a.astype('uint8'))
								if display:
									cv.ShowImage("darkframe_substracted",PIL2Ipl(swapRGB(pi_dfsub)))
									cv.ShowImage("darkframe",PIL2Ipl(swapRGB(df_im)))

							if whiteframe:
								# divide frame by normalized grey(white) frame
								c = a/((b.astype('float')+1)/256)
								d = c*(c < 255)+255*np.ones(np.shape(c))*(c > 255)
								e = d.astype('uint8')
								pi = Image.fromarray(e)					
								#pi = divideImage(pi_dfsub, gf_im)
								pi_calib = pi
								if display:
									cv.ShowImage("final_frame",PIL2Ipl(swapRGB(pi_calib)))
									cv.ShowImage("grey_orig",PIL2Ipl(swapRGB(gf_im)))
									cv.ShowImage("grey_normalized",PIL2Ipl(swapRGB(gf_im_n)))
								#cv.ShowImage("grey2",PIL2Ipl(swapRGB(gf_im_n2)))
							
							if display:														
								cv.ShowImage("original_frame",PIL2Ipl(swapRGB(img_frame)))

						# crop image
						if crop:
							pi = pi.crop( (0,0,pi.size[0],pi.size[1]-crop) )

						# stretching	
						if stretch != 1:
							pi = pi.resize( (pi.size[0], pi.size[1] *stretch), Image.ANTIALIAS)

						# apply gamma
						if gamma != -1:
							pi = imageGamma(pi, (gamma,gamma,gamma))
							
						# rotate image
						pi = pi.rotate(90)
						if ratio != 1:
							pi = pi.resize((pi.size[0] * ratio,pi.size[1] * ratio), Image.ANTIALIAS)

						# if jpg swap RGB
						#if jp4:
							#pi = swapRGB(pi)							
										
						# add frame - if full save logs
						isFull =  slitscanner.addFrame(pi)

						# preview display	
						if display:
							scale = out_w / float(screen[0])
							if out_h / float(screen[1]) > scale:
								scale = out_h / float(screen[1])
							if scale < 1:
								scale = 1
							tile = swapRGB(slitscanner.getImage())
							cv_im =  PIL2Ipl(
							tile.resize( (tile.size[0]/scale, tile.size[1]/scale), Image.NEAREST))
							#now show
							cv.ShowImage("preview",cv_im)
							if flag_calibration:
								ts = 24
								cv.MoveWindow("original_frame",0,cv_im.height + ts)
								cv.MoveWindow("darkframe_substracted",0,cv_im.height + (frame.height+ts) + ts)
								cv.MoveWindow("final_frame",0,cv_im.height + 2* (frame.height+ts) + ts)
								cv.MoveWindow("darkframe",0,cv_im.height + 3*(frame.height+ts) + ts)
								cv.MoveWindow("grey_normalized",0,cv_im.height + 4*(frame.height+ts) + ts)
								#cv.MoveWindow("grey2",0,cv_im.height + 5*(frame.height+ts) + ts)
								cv.MoveWindow("grey_orig",0,cv_im.height + 5*(frame.height+ts) + ts)
							cv.WaitKey(10)
					
						if verbose:
							print "processing frame #%05d (#%05d) (%s) to file: %s" % \
							 (framecount, totalframecount, moviefile, slitscanner.getFileName())

						# process GPS logs
						if write_log_files:
							pattern1 = "none";
							pattern2 = "1970-01-01T00:00:00.0Z"
							
							while int(line[0]) < framecount and not noMoreLogLine:							
								try:
									last_line = line
									line = logreader.next()								
									noMoreLogLine = False							
								except:
									print "no more log lines"
									noMoreLogLine = True
									
							if int(line[0]) == framecount and len(line)>14 and not re.search(pattern1, line[2]) and not re.search(pattern2, line[1]):
									

								tmp = line[:]
								tmp[0] = px_pos - offset
								logwriter.writerow(tmp)
								
								gpxalltrackwriter.addTrackpoint(
									float(line[3]), float(line[4]),
									line[1], float(line[5]), float(line[6]),
									line[2], "", line[0]
								)
								gpxwriter.addTrackpoint(
									float(line[3]), float(line[4]),
									line[1], float(line[5]), float(line[6]),
									line[2], "", line[0]
								)
								infowriter.addPoint(
									float(line[3]), float(line[4]),
									line[1], float(line[5]), float(line[6])								
								)
								infoallwriter.addPoint(	
									float(line[3]), float(line[4]),
									line[1], float(line[5]), float(line[6])								
								)
							else:
								print "discarding corrupted log line", len(line)
								print int(line[0]), framecount				

							if isFull:
								logwriter = csv.writer(
									open(
										slitscanner.getFileName() + ".log",
										"wb"),
									delimiter=";")
								gpxwriter.save()
								gpxalltrackwriter.save()
								gpxwriter.open(slitscanner.getFileName() + ".gpx")
								dist = dist +  infowriter.getDist()
								infowriter.save()
								infoallwriter.save()
								infowriter.open(slitscanner.getFileName() + ".info.txt")
								slitcount = 0
								imgcount += 1
								isFull = False
													
							if verbose and len(line)>14:
								print "log gps position #%05d px: %d, %0.4f %0.4f %s distance: %0.3fkm" % \
									(totalframecount, px_pos - offset, float(line[3]), float(line[4]), line[1],
									 (dist + infowriter.getDist()) / 1000)						 

				# read next frame
				frame =  cv.QueryFrame(movie)
				framecount += 1
				slitcount += 1
				totalframecount += 1
		
		if write_log_files:
			gpxwriter.save()
			gpxalltrackwriter.save()
			infowriter.save()
			infoallwriter.save()

	# save last image
	if not slitscanner.fileExists():
		slitscanner.saveImage()
