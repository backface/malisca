#!/usr/bin/env python
#######################################
#
# some always needed helpers
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

import os
import cv
from PIL import Image, ImageMath

def checkPath(path):
	if os.path.isdir(path):
		return True
	else:
		if not os.path.isdir(os.path.dirname(path)) and not os.path.dirname(path) == "":
			checkPath(os.path.dirname(path))
		os.mkdir(path)

def createPath(file):
	checkPath(os.path.dirname(file))

def Ipl2PIL(im):
	return Image.fromstring("RGB", cv.GetSize(im), im.tostring())

def PIL2Ipl(pi):
	cv_im = cv.CreateImage(pi.size, cv.IPL_DEPTH_8U, 3)
	cv.SetData(cv_im, pi.tostring())
	return cv_im

def swapRGB(im):
	b, g, r = im.split()
	return Image.merge("RGB", (r, g, b))

def imageGamma(img, g=(1.0,1.0,1.0), depth=256):
	"Apply a gamma curve to image"
	ret=img
	if g!=(1.0,1.0,1.0):
		(rg,gg,bg)=g
		rtable=map(lambda x: int(depth* (float(x)/depth)**(1.0/rg)), range(depth))
		gtable=map(lambda x: int(depth* (float(x)/depth)**(1.0/gg)), range(depth))
		btable=map(lambda x: int(depth* (float(x)/depth)**(1.0/bg)), range(depth))
		table=rtable+gtable+btable
		ret=img.point(table)
		return ret


def divideImage(imgA,imgB):
	# split RGB images into 3 channels
	rA, gA, bA = imgA.split()
	rB, gB, bB = imgB.split()

	# divide each channel (image1/image2)
	rTmp = ImageMath.eval("int(a/((float(b))/256))", a=rA, b=rB).convert('L')
	gTmp = ImageMath.eval("int(a/((float(b))/256))", a=gA, b=gB).convert('L')
	bTmp = ImageMath.eval("int(a/((float(b))/256))", a=bA, b=bB).convert('L')

	# merge channels into RGB image
	imgOut = Image.merge("RGB", (rTmp, gTmp, bTmp))
	return imgOut

def normalizeImage(im):
	# split RGB images into 3 channels
	rr, gg, bb = im.split()

	rTmp = ImageMath.eval("int(a*((float(255/max(a,b)))))", a=rr, b=rr).convert('L')
	gTmp = ImageMath.eval("int(a*((float(255/max(a,b)))))", a=gg, b=gg).convert('L')
	bTmp = ImageMath.eval("int(a*((float(255/max(a,b)))))", a=bb, b=bb).convert('L')
		
	# merge channels into RGB image
	imgOut = Image.merge("RGB", (rTmp, gTmp, bTmp))
	return imgOut
	
def substractImage(imgA,imgB):
	rA, gA, bA = imgA.split()
	rB, gB, bB = imgB.split()

	rTmp = ImageMath.eval("a-b", a=rA, b=rB).convert('L')
	gTmp = ImageMath.eval("a-b", a=gA, b=gB).convert('L')
	bTmp = ImageMath.eval("a-b", a=bA, b=bB).convert('L')
	
	# merge channels into RGB image
	imgOut = Image.merge("RGB", (rTmp, gTmp, bTmp))
	return imgOut
	


