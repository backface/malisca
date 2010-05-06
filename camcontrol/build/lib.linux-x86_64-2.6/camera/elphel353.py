import urllib2
import socket
import logging
import time
from xml.dom import minidom

class Camera(object):	
	def __init__(self, ip):
		self.IP = ip
		self.max_width = 2592
		self.max_height = 1936
		self.trigger = False
		self.FPS = 10
		self.params = {}
		self.gain = 0
		self.blacklevel = 10
		self.gamma = 0.57
				
		# configure socket timeout
		timeout = 10
		socket.setdefaulttimeout(timeout)

		# confifure logging
		logging.basicConfig(level=logging.DEBUG)	
		self.logger = logging.getLogger('Camera Elphel353')	


	def setFPS(self, value):
		self.FPS = value
		if self.trigger == False:
			self.setParam("FPSFLAGS", "2")
			return self.setParam("FP1000SLIM", str(value * 1000))
		else:
			trig_period = 96000000. / value * 2
			return self.setParam("TRIG_PERIOD", str(trig_period))	

		
	def setWidth(self,value):
		self.setParam("WOI_WIDTH", str(value))
		return self.setParam("WOI_LEFT", str((self.max_width - value)/2) )

		
	def setHeight(self,value):
		self.setParam("WOI_HEIGHT", str(value))
		return self.setParam("WOI_TOP", str((self.max_height - value)/2) )	

		
	def setExposure(self,value):
		return self.setParam("EXPOS", str(value * 1000))


	def setGamma(self,value):
		self.gamma = value
		return self.sendHTTPRequest("camvc.php?set=0/gam:"
			+ str(self.gamma)
			+ "/pxl:" + str(self.blacklevel)
			+ "/")


	def setBlacklevel(self,value):
		self.blacklevel = value
		return self.sendHTTPRequest("camvc.php?set=0/gam:"
			+ str(self.gamma)
			+ "/pxl:" + str(self.blacklevel)
			+ "/" )


	def setGain(self,value):
		self.gain = value
		return self.sendHTTPRequest("camvc.php?set=0/gg:"
			+ str(self.gain)
			+ "/ggb:" + str(self.gain)
			+ "/")		


	def setSaturationBlue(self, value):
		return  self.setParam("COLOR_SATURATION_BLUE", str(value))


	def setSaturationRed(self, value):
		return  self.setParam("COLOR_SATURATION_RED", str(value))


	def setRGLevel(self, value):
		return  self.setParam("RSCALE", str(value))


	def setBGLevel(self, value):
		return  self.setParam("BSCALE", str(value))						

		
	def setQuality(self,value):
		return  self.setParam("QUALITY", str(value))		


	def setTrigger(self, value):
		if value == True:			
			self.trigger = True
			self.setFPS(self.getFPS())
			return self.setParam("TRIG", "4")
		else:
			self.trigger = True
			ret = self.setParam("TRIG", "0")
			self.setFPS(self.getFPS())
			return ret


	def setFlipH(self,value):
		if value == True:			
			return self.setParam("FLIPH", "1")
		else:
			return self.setParam("FLIPH", "0")


	def setFlipV(self,value):
		if value == True:			
			return self.setParam("FLIPV", "1")
		else:
			return self.setParam("FLIPV", "0")			


	def setAutoExposureOff(self):
		return self.setParam("AUTOEXP_ON","0")	

		
	def setAutoExposureOn(self):
		return self.setParam("AUTOEXP_ON","1")


	def setAutoWhiteBalanceOff(self):
		return self.setParam("WB_EN","0")	

		
	def setAutoWhiteBalanceOn(self):
		return self.setParam("WB_EN","1")		

			
	def startStream(self):
		return self.setParam("DAEMON_EN_STREAMER","1")

		
	def stopStream(self):
		return self.setParam("DAEMON_EN_STREAMER","0")


	def streamMulticast(self):
		return self.setParam("STROP_MCAST_EN","1")


	def streamUnicast(self):
		return self.setParam("STROP_MCAST_EN","1")			

		
	## general methods
	def rebootCam(self):
		return self.sendHTTPRequest("phpshell.php?command=reboot%20-f")

		
	def setParam(self, param, value):
		self.sendHTTPRequest("setparam.php?" + param + "=" + value)
		
		
	def getParamsFromCAM(self):
		url = "getParams.php" 
		data = self.sendHTTPRequest(url)
		
		if data:
			self.logger.debug(data )
		
			xmldoc = minidom.parseString(data)
			cameraNode = xmldoc.firstChild		
			valNodes = cameraNode.childNodes
			valNodes.pop(0)			
		
			for valNode in valNodes:
				
				#self.logger.debug("%s %s %s" % (valNode.nodeName,valNode.nodeValue,valNode.nodeType) )
				if valNode.nodeType == 3:
					print valNode.data
				#	print "x"
				#	key = valNode.tagName
				#	value = valNode.firstChild.data					
				#	self.params[key] = value	
						
					
	def sendHTTPRequest(self, url):
		#return True
		url = "http://%s/%s" % (self.IP, url)
		req = urllib2.Request(url)
		self.logger.debug("REQUEST: %s" % (url) )	
		
		try:
			f = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			self.logger.warning("The server couldn\'t fulfill the request. %s" % time.strftime("%Y/%m/%d %H:%M:%S"))
			self.logger.warning('Error: %s', e)
			return False
		except urllib2.URLError, e:
			self.logger.warning("We failed to reach a server. %s" % time.strftime("%Y/%m/%d %H:%M:%S"))
			self.logger.warning("Reason: %s" % e.reason)
			return False
		except socket.error, e:
			self.logger.warning("Socket timout. %s" % time.strftime("%Y/%m/%d %H:%M:%S"))
			self.logger.warning("Reason: %s" % e)
			return False	
		except KeyboardInterrupt:
			exit(0)
			return False		
		except: 
			self.logger.warning("Unexpected error: %s", sys.exc_info()[0])
			return False			
		else:
			ret = f.read()
			return ret


if __name__ == '__main__':
    cam = Camera()
    cam.stopStream()
    cam.getParamsFromCAM()
    cam.setSize(800,600)
    cam.startStream()
    print cam.getSize()

