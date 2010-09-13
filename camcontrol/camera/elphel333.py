#
# Camera control class for Elphel333
# (c) 2010 Michael Aschauer
#

import urllib2
import socket
import logging
import time
from xml.dom import minidom

class Camera(object):

	def __init__(self,ip="192.168.0.9"):
		self.ip = ip		
		self.img_src = "http://%s/admin-bin/ccam.cgi?opt=vhcxym" % self.ip
		self.video_src = "rtsp://%s:554" % self.ip
		self.max_width = 2048
		self.max_height = 1536		
				
		self.FPS = 0			
		self.QUALITY = 0
		self.EXPOSURE = False		
		self.STREAMER_ON = False
		self.STREAMER_MULTICAST = False		
		self.SENSOR_STATE = 0
		self.streaming = True
		self.pf_height = 64
		self.params = {}
		self.exposureParams = {}
		self.Photofinish = False
		
		# configure socket timeout
		timeout = 3
		socket.setdefaulttimeout(timeout)
		
		logging.basicConfig(level=logging.DEBUG)	
		self.logger = logging.getLogger('Camera Elphel333')
		
		self.getParamsFromCAM()
		self.FPS = self.getFPS()
		self.QUALITY = self.getQuality()
		self.getExposureParamsFromCAM()


	def getFPS(self):
		if self.params.has_key("FPS"):
			return float(self.params["FPS"]);
		else:
			return 0

		
	def setFPS(self, value):
		self.params["FPS"]=value
		self.FPS=value
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&fps=%s" % value) 


	def setHeight(self,val):
		self.stopStream()
		top = ( int(self.params["P_SENSOR_HEIGHT"]) - val) / 2
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhxc&wh=%s&wt=%s"
			% (val,top))
		time.sleep(1)
		self.startStream()

	
	def getHeight(self):
		if self.params.has_key("P_WOI_HEIGHT"):
			return int(self.params["P_WOI_HEIGHT"])
		else:
			return 0


	def setWidth(self,val):
		self.stopStream()
		top = ( int(self.params["P_SENSOR_WIDTH"]) - val) / 2
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhxc&ww=%s&wl=%s"
			% (val, top))
		time.sleep(1)
		self.startStream()

						
	def getWidth(self):
		if self.params.has_key("P_WOI_WIDTH"):
			return int(self.params["P_WOI_WIDTH"])
		else:
			return 0

		
	def setExposure(self,value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u+&e=%s" % (value) )


	def getExposure(self):
		if self.params.has_key("P_EXPOS"):
			return float(self.params["P_EXPOS"])
		else:
			return 0

		
	def startStream(self):
		time.sleep(1)
		transport = self.params["S_name"]
		self.sendHTTPRequest("sctl.cgi?cmd=start&transport="+transport+"&addr=232.0.0.1&port=20000&fps="+self.params["FPS"])	
		self.getParamsFromCAM()
		self.streaming = True

		
	def stopStream(self):
		self.sendHTTPRequest("sctl.cgi?cmd=stop")
		self.getParamsFromCAM()
		self.streaming = False


	def getStreamerStatus(self):
		if self.params.has_key("S_STREAM"):
			return int(self.params["S_STREAM"]) > 0
		else:
			return False


	def streamMulticast(self):					
		self.params["S_name"] == "mcast"
		if int(self.params["S_STREAM"]) > 0:
			self.stopStream()
			self.startStream()


	def streamUnicast(self):
			self.params["S_name"] == "unicast"


	def getMulticastStatus(self):
		if self.params.has_key("S_name"):
			if self.params["S_name"] == "unicast":
				return False
			else:
				return True
		else:
			return False

		
	def setAutoExposureOff(self):
		self.sendHTTPRequest("/autoexpos.cgi?reg=1&onoff=0")	
		self.getParamsFromCAM()	

		
	def setAutoExposureOn(self):
		self.sendHTTPRequest("/autoexpos.cgi?reg=1&onoff=1")	
		self.getParamsFromCAM()


	def getAutoExposureStatus(self):
		return int(self.exposureParams["AEONOFF"])		

		
	def setQuality(self,val):
		self.stopStream()
		self.params["P_QUALITY"] = val
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhxc&iq=%s" % (val))
		self.startStream()	

					
	def getQuality(self):
		if self.params.has_key("P_QUALITY"):
			return int(self.params["P_QUALITY"])
		else:
			return 0


	def setGain(self,v):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&gr=%s&gg=%s&gb=%s&ggb=%s" % (v,v,v,v))


	def getGain(self):
		if self.params.has_key("P_GAINR"):
			return float(self.params["P_GAINR"])
		else:
			return 0	


	def getBlacklevel(self):
		if self.params.has_key("P_PIXEL_LOW"):
			return float(self.params["P_PIXEL_LOW"])
		else:
			return 0

		
	def setBlacklevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&pxl=%s" % value) 


	def getWhitelevel(self):
		if self.params.has_key("P_PIXEL_HIGH"):
			return float(self.params["P_PIXEL_HIGH"])
		else:
			return 0

		
	def setWhitelevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&pxh=%s" % value) 


	def getGamma(self):
		if self.params.has_key("P_GAMMA"):
			return float(self.params["P_GAMMA"])/100.
		else:
			return 0

		
	def setGamma(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&gam=%s" % (float(value)*100.))


	def getSaturationRed(self):
		if self.params.has_key("P_COLOR_SATURATION_RED"):
			return float(self.params["P_COLOR_SATURATION_RED"])
		else:
			return 0			

		
	def setSaturationRed(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&csr=%s" % value)


	def getSaturationBlue(self):
		if self.params.has_key("P_COLOR_SATURATION_BLUE"):
			return float(self.params["P_COLOR_SATURATION_BLUE"])
		else:
			return 0			


	def setSaturationBlue(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&csb=%s" % value) 		

		
	def setRGLevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&rscale=%s" % value)


	def getRGLevel(self):
		if self.params.has_key("P_RSCALE"):
			return float(self.params["P_RSCALE"])
		else:
			return 0			


	def setBGLevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&bscale=%s" % value)


	def getBGLevel(self):
		if self.params.has_key("P_BSCALE"):
			return float(self.params["P_BSCALE"])
		else:
			return 0			


	def setAutoWhiteBalance(self):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&bscale=auto&rscale=auto")
		self.getParamsFromCAM()


	def setFlipH(self):
		# not yet
		return 0


	def setFlipV(self):
		# not yet
		return 0
		

	def getSensorState(self):
		return self.params["SENSOR_STATE"]


	def getPhotoFinishState(self):
		if self.params.has_key("P_PF_HEIGHT"):
			return int(self.params["P_PF_HEIGHT"]) > 1
		else:
			return False


	def startPhotofinish(self):
		self.Photofinish = True
		w = self.getWidth()
		h = 64 #self.getHeight()
		left = ( int(self.params["P_SENSOR_WIDTH"]) - w) / 2
		top = ( int(self.params["P_SENSOR_HEIGHT"]) - h) / 2
		fps = self.getFPS()
		
		self.stopStream()
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhcxmuy+!&pfh=2ww=%s&wh=%s&wl=%s&wt=%s&fps=%s&dh=1&dv=1&iq=%s"
			% (w,h,left,top,self.getFPS(), self.getQuality() ) )
		time.sleep(1)
		self.startStream()


	def startNormalMode(self):
		self.Photofinish = False
		w = self.getWidth()
		h = self.getHeight()
		left = ( int(self.params["P_SENSOR_WIDTH"]) - w) / 2
		top = ( int(self.params["P_SENSOR_HEIGHT"]) - h) / 2
		fps = self.getFPS()
		
		self.stopStream()
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhcxmuy+!&pfh=0&ww=%s&wh=%s&wl=%s&wt=%s&fps=%s&dh=1&dv=1&iq=%s"
			% (w,h,left,top,self.getFPS(), self.getQuality() ) )
		time.sleep(1)
		self.startStream()

		
	def getParamsFromCAM(self):
		url = "admin-bin/ccam.cgi?html=10" 
		data = self.sendHTTPRequest(url)
		
		if data:
			#self.logger.debug(data)		
			xmldoc = minidom.parseString(data)
			cameraNode = xmldoc.firstChild		
			valNodes = cameraNode.childNodes
			valNodes.pop(0)
		
			for valNode in valNodes:
				if valNode.firstChild.nodeType == valNode.firstChild.TEXT_NODE:
					key = valNode.tagName
					value = valNode.firstChild.data
					self.params[key] = value
					self.logger.debug("read param %s: %s" % (key,value))
			return True
		else:
			return False
			
					
	def getExposureParamsFromCAM(self):
		url = "autoexpos.cgi?reg=2" 
		data = self.sendHTTPRequest(url)
		
		if data:
			#self.logger.debug(data )		
			xmldoc = minidom.parseString(data)
			cameraNode = xmldoc.firstChild		
			valNodes = cameraNode.childNodes
			valNodes.pop(0)
		
			for valNode in valNodes:
				if valNode.firstChild:
					key = valNode.tagName
					value = valNode.firstChild.data
					self.exposureParams[key] = value
					self.logger.debug("read exposure param %s: %s" % (key,value))

			return True
		else:
			return False

					
	def sendHTTPRequest(self, url):		
		url = "http://%s/%s" % (self.ip, url)
		req = urllib2.Request(url)
		self.logger.debug("REQUEST: %s" % (url) )	
		
		try:
			f = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			self.logger.warning("The server couldn\'t fulfill the request. %s" % time.strftime("%Y/%m/%d %H:%M:%S"))
			self.logger.warning('Error: %s', e)
			return False
		except urllib2.URLError, e:
			self.logger.warning("Failed to reach camera %s on %s" % (self.ip, time.strftime("%Y/%m/%d %H:%M:%S")))
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
			return f.read()
			

	def rebootCam(self):
		try:
			os.system("reboot333")
		except:
			self.logger.warning("could not run reboot script.missing?")

	def requestImage(self):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhcxym")
		self.getParamsFromCAM()			


