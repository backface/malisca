#!/usr/bin/env python
#######################################
#
# simple and stupid slitscanner
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

from PIL import Image
import myutils
import os

class SlitScanner:

	def __init__(self, width=2):
		self.slitWidth = width
		self.path = "scan-data"
		self.width = 512
		self.height  = 512
		self.scan_img = Image.new( \
			"RGB",(self.width, self.height), 
			(255,255,255))
		self.img_count = 1
		self.frame_count = 0
		self.slit_count = 0
		self.overwrite = True
		self.filetype = "JPEG"
		self.extensions = {
			"PNG":"png",
			"JPEG":"jpg",
			"TIFF":"tif" }
		self.quality = 98
		self.reverse = False
		self.prefix = "img"

	def setOverwriteExisting(b):
		self.overwrite = b

	def setPath(self, path):
		self.path = path

	def setReverse(self, b):
		self.reverse = b

	def setFileType(self,type):
		self.filetype = type

	def setSlitWidth(self, w):
		self.slitWidth = w

	def setJPEGQuality(self, q):
		self.quality = q

	def setSize(self, w, h):
		self.width = w
		self.height = h
		self.scan_img = scan_img = Image.new( \
			"RGB",(self.width, self.height), 
			(255,255,255) )

	def setFilePrefix(self, n):
		self.prefix = n

	def getFilePrefix(self):
		return self.prefix
		
	def getFileName(self):
		scan_file = "%s.%s" % \
			(self.getFileBaseName(), self.extensions[self.filetype])
		return scan_file

	def getFileBaseName(self):
		if self.reverse:
			counter = 10000 - self.img_count
		else:
			counter = self.img_count
		scan_file = "%s/%dx%d/%s-%06d" % \
			(self.path, self.width, self.height, self.prefix, counter)
		return scan_file
		
	def getFileDirectory(self):
		scan_dir = "%s/%dx%d/" % \
			(self.path, self.width, self.height)
		return scan_dir		
		
	def addFrame(self, img):
		slit = img.crop( (
			(img.size[0]/2 - self.slitWidth/2),
			0,
			(img.size[0]/2 - self.slitWidth/2 + self.slitWidth),
			img.size[1]
			) )

		if self.reverse:
			slit = slit.transpose(Image.FLIP_LEFT_RIGHT)
			self.scan_img.paste(slit,
			(self.width - (self.slit_count * self.slitWidth + self.slitWidth), 0,
			 self.width - (self.slit_count * self.slitWidth), self.height ) )			
		else:			
			self.scan_img.paste(slit,
			(self.slit_count * self.slitWidth, 0,
			 self.slit_count * self.slitWidth + self.slitWidth, self.height ) )
			 
		if (self.slit_count + 1) * self.slitWidth >= self.width:
			self.saveImage()
			self.scan_img = Image.new("RGB",(self.width,self.height),(255,255,255))
			self.img_count +=1
			self.slit_count = 0
			return True
		else:
			self.frame_count += 1
			self.slit_count += 1
			return False

	def addButDontScanFrame(self):
		if (self.slit_count + 1) * self.slitWidth >= self.width:
			self.img_count +=1
			self.slit_count = 0
			return True
		else:
			self.frame_count += 1
			self.slit_count += 1
			return False

	def getImage(self):
		return self.scan_img

	def getPixelInImage(self):
		return (self.slit_count + 1)

	def getPixelInScan(self):
		return (self.img_count - 1)  * self.width + (self.slit_count + 1)
		
	def fileExists(self):
		return os.path.exists(self.getFileName())
		
	def saveImage(self):
		scan_file = self.getFileName()
		myutils.createPath(scan_file)
		print "saving file:", scan_file
		if self.filetype == "JPEG":
			self.scan_img.save(scan_file,self.filetype,quality=self.quality)
		else:
			self.scan_img.save(scan_file,self.filetype)
		self.scan_img = Image.new("RGB",(self.width,self.height),(255,255,255))		
	
		
			
