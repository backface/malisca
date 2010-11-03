#!/usr/bin/env python
#######################################
#
# generate a vrt file of long strips for gdal2tiles
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################


import glob, sys
import getopt
from PIL import Image


greyscale = False
input = "*.tif"
output = "tileset.vrt"


def usage():
	print """
usage: riverscan.py -i TRACKFILE.gpx [-i FILE.gpx ..] [options]

linescan over map data along a gps track

options:
    -h, --help              print usage
    -i, --input=FILE        input files
    -o, --output=FILE       output.file
    -f, --format=FORMAT     image format for cache and output
    -g, --greyscale		
"""

def process_args():
	global input, output, format, greyscale
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:g",
			["help", "input=","output=","greyscale"])
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
		elif o in ("-g","--greyscale"):
			greyscale = True	
		else:
			assert False, "unhandled option"
		

if __name__ == "__main__":

	process_args()


	if greyscale:
		bands = [""]
		bandtypes = ["Grey"]
	else:
		bands = ["","",""]
		bandtypes = ["Red","Green","Blue"]

	vrt_file = output
	meta_file = "%s.json" % output.split(".")[0]	
		
	count = 0
	leng = 0

	files = glob.glob(input)
	files.sort()
	
	if files == []:
		print "no files found for", input
		exit()
	
	for file in files:
		img = Image.open(file)
		w = img.size[0]
		h = img.size[1]
		x = count * w
		y = count * h

		leng += w

		source_content = '''
       <SourceFilename relativeToVRT="1">%s</SourceFilename>
       <SourceProperties RasterXSize="%d" RasterYSize="%d" DataType="Byte"/>
       <SrcRect xOff="0" yOff="0" xSize="%d" ySize="%d"/>
       <DstRect xOff="%d" yOff="0" xSize="%d" ySize="%d"/>''' \
		% (file, w, h, w, h, x, w, h)		

		for i in range(0,len(bands)):
			source_tag = '''
     <SimpleSource>
       <SourceBand>%d</SourceBand>%s
     </SimpleSource>\n''' % (i+1, source_content)	
			bands[i] += source_tag
		
		count += 1

	# now write to files	

	i = 0

	# write vrt
	f = open(vrt_file, 'w')	
	f.write('<VRTDataset rasterXSize="%d" rasterYSize="%d">\n' % (leng, h))
	for band in bands:
		f.write('''  <VRTRasterBand dataType="Byte" band="%d">
     <ColorInterp>%s</ColorInterp>\n''' % (i+1, bandtypes[i]))
		f.write(band)
		f.write('\n  </VRTRasterBand>\n')
		i += 1
	f.write('</VRTDataset>')
	f.close()

	# write bounds to meta file
	import json
	f = open(meta_file, "w")
	f.write(json.dumps({
		"bounds":[0, -h, leng, 0],\
		"height": h,
		"width":leng,
		},
		indent=4, sort_keys=True))
	f.write("\n")
	#f.write("%f, %f, %f, %f\n" % (0, -h, len, 0) )
	f.close()
