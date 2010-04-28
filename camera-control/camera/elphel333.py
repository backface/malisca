import urllib2
import socket
import logging
import time
from xml.dom import minidom

class Camera(object):	
	def __init__(self,ip="192.168.0.9"):
		self.IP = ip
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
		self.logger = logging.getLogger('Camera Elphel353')
		
		self.getParamsFromCAM()
		self.FPS = self.params["FPS"]
		self.QUALITY = self.params["P_QUALITY"]
		self.getExposureParamsFromCAM()
						
	def getFPS(self):
		return float(self.params["FPS"]);
		
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
		return int(self.params["P_WOI_HEIGHT"])	

	def setWidth(self,val):
		self.stopStream()
		top = ( int(self.params["P_SENSOR_WIDTH"]) - val) / 2
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhxc&ww=%s&wl=%s"
			% (val, top))
		time.sleep(1)
		self.startStream()
						
	def getWidth(self):
		return int(self.params["P_WOI_WIDTH"])			
		
	def setExposure(self,value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u+&e=%s" % (value) )

	def getExposure(self):
		return float(self.params["P_EXPOS"])
		
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
		if(self.params["S_name"] == "unicast"):
			return False
		else:
			return True
		
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
		return int(self.params["P_QUALITY"])

	def setGain(self,v):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&gr=%s&gg=%s&gb=%s&ggb=%s" % (v,v,v,v))

	def getGain(self):
		return float(self.params["P_GAINR"])		

	def getBlacklevel(self):
		return float(self.params["P_PIXEL_LOW"]);
		
	def setBlacklevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&pxl=%s" % value) 

	def getWhitelevel(self):
		return float(self.params["P_PIXEL_HIGH"]);
		
	def setWhitelevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&pxh=%s" % value) 

	def getGamma(self):
		return float(self.params["P_GAMMA"])/100.
		
	def setGamma(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&gam=%s" % (float(value)*100.))

	def getSaturationRed(self):
		return float(self.params["P_COLOR_SATURATION_RED"]);
		
	def setSaturationRed(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&csr=%s" % value)

	def getSaturationBlue(self):
		return float(self.params["P_COLOR_SATURATION_BLUE"]);

	def setSaturationBlue(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&csb=%s" % value) 		
		
	def setRGLevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&rscale=%s" % value)

	def getRGLevel(self):
		return float(self.params["P_RSCALE"]);

	def setBGLevel(self, value):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&bscale=%s" % value)

	def getBGLevel(self):
		return float(self.params["P_BSCALE"]);

	def setAutoWhiteBalance(self):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=u&bscale=auto&rscale=auto")
		self.getParamsFromCAM()

	def requestImage(self):
		self.sendHTTPRequest("admin-bin/ccam.cgi?opt=vhcxym")
		self.getParamsFromCAM()					


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
			return f.read()
			
			

if __name__ == '__main__':
    cam = Camera()
    cam.stopStream()
    cam.getParamsFromCAM()
    cam.setSize(800,600)
    cam.startStream()
    print cam.getSize()

