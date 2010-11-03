#
# Camera control class for Elphel353
# (c) 2010 Michael Aschauer
#

import urllib2
import socket
import logging
import time
from xml.dom import minidom

class Camera(object):	
	def __init__(self, ip):
		self.ip = ip

		self.img_src = "http://%s:8081/bimg" % self.ip
		self.video_src = "rtsp://%s:554" % self.ip

		self.params = {}
		
		self.trigger = False
		self.params = {}
		self.params["GAIN"] = 0
		self.params["GAMMA"] = 0.54
		self.params["BLACKLEVEL"] = 10
		self.params["SENSOR_WIDTH"] = 2592
		self.params["SENSOR_HEIGHT"] = 1936		
				
		# configure socket timeout
		timeout = 10
		socket.setdefaulttimeout(timeout)

		# confifure logging
		logging.basicConfig(level=logging.DEBUG)	
		self.logger = logging.getLogger('Camera Elphel353')

		self.getParamsFromCAM()


	def setFPS(self, value):
		self.FPS = value
		# set trigger
		trig_period = 96000000. / value * 2
		setfps = str(value * 1000.0)
		#self.setParam("TRIG_PERIOD", str(trig_period))
		#self.setParam("FPSFLAGS", "2")
		#return self.setParam("FP1000SLIM", str(value * 1000))
		self.sendHTTPRequest("setparams.php?FPSFLAGS=2&framedelay=1&TRIG_PERIOD=%f&FP1000SLIM=%f" %(trig_period, value * 1000))
		
	def getFPS(self):
		if self.getTrigger():
			print self.params["TRIG_PERIOD"]
			if self.params.has_key("TRIG_PERIOD"):
				return (96000000.) / (float(self.params["TRIG_PERIOD"]))
			else:
				return 0			
		else:
			if self.params.has_key("FP1000SLIM"):
				return int(self.params["FP1000SLIM"]) / 1000
			else:
				return 0

	def getMaxWidth(self):
		if self.params.has_key("SENSOR_WIDTH"):
			return int(self.params["SENSOR_WIDTH"])
		else:
			return 0

	def getMaxHeight(self):
		if self.params.has_key("SENSOR_HEIGHT"):
			return int(self.params["SENSOR_HEIGHT"])
		else:
			return 0			
		
	def setWidth(self,value):
		self.setParam("WOI_WIDTH", str(value))
		return self.setParam("WOI_LEFT", str((self.getMaxWidth() - value)/2) )

	def getWidth(self):
		if self.params.has_key("WOI_WIDTH"):
			return int(self.params["WOI_WIDTH"])
		else:
			return 0		
		
	def setHeight(self,value):
		self.setParam("WOI_HEIGHT", str(value))
		return self.setParam("WOI_TOP", str((self.getMaxHeight() - value)/2) )	

	def getHeight(self):
		if self.params.has_key("WOI_HEIGHT"):
			return int(self.params["WOI_HEIGHT"])
		else:
			return 0
		
	def setExposure(self,value):
		return self.setParam("EXPOS", str(value * 1000))

	def getExposure(self):
		if self.params.has_key("EXPOS"):
			return float(self.params["EXPOS"]) / 1000
		else:
			return 0


	def setGamma(self,value):
		self.params["GAMMA"] = value
		return self.sendHTTPRequest("camvc.php?set=0/gam:"
			+ str(self.params["GAMMA"])
			+ "/pxl:" + str(self.params["BLACKLEVEL"])
			+ "/")

	def getGamma(self):
		return self.params["GAMMA"]		

	def setBlacklevel(self,value):
		self.params["BLACKLEVEL"] = value
		return self.sendHTTPRequest("camvc.php?set=0/gam:"
			+ str(self.params["GAMMA"])
			+ "/pxl:" + str(self.params["BLACKLEVEL"])
			+ "/" )

	def getBlacklevel(self):
		return int(self.params["BLACKLEVEL"])


	def setGain(self,value):
		self.params["GAIN"] = value
		return self.sendHTTPRequest("camvc.php?set=0/gg:"
			+ str(self.params["GAIN"])
			+ "/ggb:" + str(self.params["GAIN"])
			+ "/")		

	def getGain(self):
		return float(self.params["GAIN"])
		
	def setSaturationBlue(self, value):
		return self.setParam("COLOR_SATURATION_BLUE", str(value))

	def getSaturationBlue(self):
		return float(self.params["COLOR_SATURATION_BLUE"])

	def setSaturationRed(self, value):
		return self.setParam("COLOR_SATURATION_RED", str(value))

	def getSaturationRed(self):
		return float(self.params["COLOR_SATURATION_RED"])

	def setRGLevel(self, value):
		return  self.setParam("RSCALE", str(value* 65536) )

	def getRGLevel(self):
		return float(self.params["RSCALE"])/65536

	def setBGLevel(self, value):
		return  self.setParam("BSCALE", str(value* 65536))						

	def getBGLevel(self):
		return float(self.params["BSCALE"])/ 65536
		
	def setQuality(self,value):
		return self.setParam("QUALITY", str(value))		

	def getQuality(self):
		return int(self.params["QUALITY"])

	def getTrigger(self):
		return (int(self.params["TRIG"]) > 0)

	def setTrigger(self, value):
		if value == True:						
			fps = self.getFPS()
			self.trigger = True
			self.setFPS(fps)
			return self.setParam("TRIG", "4")
		else:
			self.trigger = False
			ret = self.setParam("TRIG", "0")
			self.setFPS(self.getFPS())
			return ret

	def setFlipH(self,value):
		if value == True:			
			return self.setParam("FLIPH", "1")
		else:
			return self.setParam("FLIPH", "0")

	def getFlipH(self):
		return (int(self.params["FLIPH"]) > 0)

	def setFlipV(self,value):
		if value == True:			
			return self.setParam("FLIPV", "1")
		else:
			return self.setParam("FLIPV", "0")

	def getFlipV(self):
		return (int(self.params["FLIPH"]) > 0)


	def setVirtKeep(self,value):
		if value == True:			
			return self.setParam("VIRT_KEEP", "1")
		else:
			return self.setParam("VIRT_KEEP", "0")
			
	def getVirtKeep(self):
		return (int(self.params["VIRT_KEEP"]) > 0)			

	def setVirtHeight(self,value):
		return self.setParam("VIRT_HEIGHT", str(value))		

	def getVirtHeight(self):
		return int(self.params["VIRT_HEIGHT"])
		
	def setAutoExposureOff(self):
		return self.setParam("AUTOEXP_ON","0")	
		
	def setAutoExposureOn(self):
		return self.setParam("AUTOEXP_ON","1")

	def getAutoExposureStatus(self):
		return int(self.params["AUTOEXP_ON"])			

	def setAutoWhiteBalanceOff(self):
		return self.setParam("WB_EN","0")	

	def setAutoWhiteBalanceOn(self):
		return self.setParam("WB_EN","1")

	def setAutoWhiteBalance(self):
		self.sendHTTPRequest("whitebalance.php")
		self.getParamsFromCAM()		

	def setColorColor(self):
		self.setParam("COLOR","1")
		self.getParamsFromCAM()		

	def setColorMono(self):
		self.setParam("COLOR","0")
		self.getParamsFromCAM()		

	def setColorJP46(self):
		self.setParam("COLOR","2")
		self.getParamsFromCAM()

	def getColorIsMono(self):
		return int(self.params["COLOR"]) == 0

	def getColorIsColor(self):
		return int(self.params["COLOR"]) == 1

	def getColorIsJP4(self):
		return int(self.params["COLOR"]) == 2		
						
	def startStream(self):
		return self.setParam("DAEMON_EN_STREAMER","1")
		
	def stopStream(self):
		return self.setParam("DAEMON_EN_STREAMER","0")

	def streamMulticast(self):
		return self.setParam("STROP_MCAST_EN","1")

	def streamUnicast(self):
		return self.setParam("STROP_MCAST_EN","0")			

	def getMulticastStatus(self):
		if self.params.has_key("STROP_MCAST_EN"):
			return int(self.params["STROP_MCAST_EN"])
		else:
			return False

	def getStreamerStatus(self):
		if self.params.has_key("DAEMON_EN_STREAMER"):
			return int(self.params["DAEMON_EN_STREAMER"]) > 0
		else:
			return False

	def getSensorState(self):
		return self.params["SENSOR_RUN"]

	def getPhotoFinishState(self):
		if self.params.has_key("PF_HEIGHT"):
			return int(self.params["PF_HEIGHT"]) > 1
		else:
			return False		

	def startPhotofinish(self):
		self.Photofinish = True
		#self.stopStream()
		#self.setParam("PF_HEIGHT","2")
		self.sendHTTPRequest("setparams.php?PF_HEIGHT=2&WOI_HEIGHT=%d" %  int(self.params["WOI_HEIGHT"]))		
		#self.startStream()

	def startNormalMode(self):
		self.Photofinish = False
		#elf.stopStream()
		#self.setParam("PF_HEIGHT","0")	
		self.sendHTTPRequest("setparams.php?PF_HEIGHT=0&WOI_HEIGHT=%d" %  int(self.params["WOI_HEIGHT"]))
		#self.startStream()		


	## general methods

	def getStreamUrl(self):
		return "rtsp://%s:554" % self.ip

	def getSnapshotUrl(self):
		return "http://%s:8081/bimg" % self.ip

	def getIP(self):
		return self.ip

	def getSnapshot(self):
		return 0	

	def rebootCam(self):
		return self.sendHTTPRequest("phpshell.php?command=reboot%20-f")

		
	def setParam(self, param, value):
		self.sendHTTPRequest("setparams.php?" + param + "=" + value +
			"&framedelay=1")
		
				
	def getParamsFromCAM(self):
		url = "getparams.php" 
		data = self.sendHTTPRequest(url)
		
		if data:
			#self.logger.debug(data)		
			xmldoc = minidom.parseString(data)
			cameraNode = xmldoc.firstChild		
			valNodes = cameraNode.childNodes
			valNodes.pop(0)
		
			for valNode in valNodes:
				if valNode.nodeType == 1:
					key = valNode.tagName
					value = valNode.firstChild.data
					self.params[key] = value
					#self.logger.debug("read param %s: %s" % (key,value))
			return True
		else:
			return False	
						
					
	def sendHTTPRequest(self, url):
		#return True
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
