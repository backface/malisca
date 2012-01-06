#!/usr/bin/env python
#######################################
#
# generate a html preview files
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################


import glob, sys, os
import getopt, csv
from PIL import Image
from libs.myutils import *
from libs.gpxwriter import GPXWriter, GeoInfoWriter
import re

greyscale = False
input = "./"
output = "./"
name = "test"
th_height = 128
process_logs = True
process_images = True
process_html = True
verbose = True
trackfile = "track.gpx"
tracklogfile = "track.log.csv"

def usage():
	print """

options:
    -h, --help              print usage
    -i, --input=DIR         input path
    -o, --output=DIR        output path
    -f, --format=FORMAT     image format for cache and output    
        --name=NAME         NAME
    -n, --nologs            dont process log files
"""

def process_args():
	global input, output, format, name, process_logs
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:nl",
			["help", "input=","output=","name=","nologs","log-only"])
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
			input=a
		elif o in ("-f", "--format"):
			format = a
		elif o in ("--name"):			
			name = a
		elif o in ("-n","--nologs"):
			process_logs = False
		elif o in ("-l","--logs-only"):
			process_logs = True
			process_images = False
			process_html = False			
		else:
			assert False, "unhandled option"
		

if __name__ == "__main__":

	process_args()

	html_file = output + "/index.html"
	thumb_path = output + "/%d/" % (th_height)
	meta_file = "%s.txt" % output.split(".")[0]	
		
	count = 0
	leng = 0

	files = glob.glob(input + "/*.jpg")
	files.sort()
	
	if files == []:
		print "no files found for", input
		exit()

	source = ""
	info = ""

	if process_logs:
		infowriter = GeoInfoWriter(output + "/info.txt")
		gpxwriter = GPXWriter(output + "/" + trackfile)
		logwriter = csv.writer(open(output + "/" + tracklogfile,"wb"),delimiter=";")
	else:
		print "don't process logs"
	
	for file in files:

		thumb_file = "%s/%s" % (thumb_path,os.path.basename(file))
		log_file = "%s.log" % file

		if process_images:
			img = Image.open(file)
			w = img.size[0]
			h = img.size[1]
			ratio = th_height / float(h)
			th_width = int(w * ratio)

		if process_logs:
			if os.path.exists(file + ".log"):
				logreader = csv.reader(open(file + ".log","rb"), delimiter=";")
				try:
					pattern1 = "none";
					pattern2 = "1970-01-01T00:00:00.0Z"
					for line in logreader:
						# discard non-valid fixes
						if not re.search(pattern1, line[2]) and not re.search(pattern2, line[1]):
							logwriter.writerow(line)
							infowriter.addPoint(
									float(line[3]), float(line[4]),
									line[1], float(line[5]), float(line[6]))
							gpxwriter.addTrackpoint(float(line[3]), float(line[4]),
									line[1], float(line[5]), float(line[6]),
									line[2],"",line[0]
								)
						else:
							print "discard non-valid gps log for at %s, fix: %s" % (line[1],line[2])
				except:
					print "x"
								
		if not os.path.exists(thumb_file) and process_images:
			# generate thumbs
			if verbose:
				print "make thumnail from %s" % os.path.basename(file)			
			img_out = img.resize((th_width,th_height),Image.ANTIALIAS)
			createPath(thumb_file)
			img_out.save(thumb_file)
						
		if process_html:
			source += '<a href="%s"><img border="0" src="%s" alt="" height="%d" width="%d" /></a>\n' % \
			(file, thumb_file, th_height, th_width)

		count+=1

	if process_logs: 
		info = infowriter.getInfoStringHTML()
		infowriter.save()
		gpxwriter.save()
		info += '&raquo;<a href="%s">trackfile</a>' % trackfile
	else:
		info = "no gps log data available."
		
	# now write to files	
	print "%d files found." % count
	if process_html:
		print "generating html.."

		# write html
		f = open(html_file, 'w')	
		f.write('''<html>
		<head>
			<title>%s</title>
			<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
			<style type="text/css" media="screen">
				body {font-family: Georgia, Times New Roman, Times, serif}
				a {padding:0px;margin:0px}
				img {padding:0px;margin:0px;margin-right:-4px;margin-top:5px}
			</style>
		<head>
		<body>
		<h2>%s</h2>
		<div id="info">%s</div>
		<div id="thumbs">
			%s
		</div>
		</html>''' % ( name, name, info, source  )
		)
		f.close()
