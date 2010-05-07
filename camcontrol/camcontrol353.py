#!/usr/bin/python 

import sys, os
import pygtk, gtk, gobject
import urllib
import gst
import logging
import cPickle

from camera.elphel353 import Camera


class CamControl:
		
	def __init__(self,ip):
		self.controls_active = False		
		self.state_file = "camcontrol353.state"
		self.fps_by_trigger = False
		self.state = {}

		logging.basicConfig(level=logging.DEBUG)	
		self.logger = logging.getLogger('GUI')		
		      
		self.builder = gtk.Builder()
		self.builder.add_from_file("camcontrol353.xml") 
		self.builder.connect_signals(self)
        
		self.window = self.builder.get_object("window")
		self.window.show()				
		self.preview_window = self.builder.get_object("preview_win")
		self.builder.get_object("statusbar").push(0,"--");
			
		self.cam = Camera(ip)
		self.videosrc = self.cam.getStreamUrl()
		self.img = self.cam.getSnapshotUrl()
		
		#self.load_state();
				
		# single image preview
		#self.image = self.builder.get_object("image")
		#self.update_image()
		# timeout for update image 
		#self.update_id = gobject.timeout_add(1000, self.update_image)
		#self.update_id = gobject.timeout_add(1000, self.ping())

		self.loadParamsFromCam()
		self.controls_active = True

		# Set up the gstreamer pipeline	for preview
		self.movie = self.builder.get_object("movie")
		self.pipeline = ""
		self.setup_pipeline()

		#353
		self.builder.get_object("blacklevel").set_value(10)			
		self.builder.get_object("gamma").set_value(0.47)
		self.builder.get_object("gain").set_value(4.0)
			
		self.update_id = gobject.timeout_add(1000, self.updateParams)		

	def loadGUI(self,file):
		try:
			self.builder.add_from_file(file)
		except glib.GError, e:
			try:
				print e
				self.builder.add_from_file("/usr/local/share/camcontrol/"+file)
			except glib.GError, e:
				try:
					print e
					self.builder.add_from_file("/usr/share/camcontrol/"+file)
				except:
					print e
					sys.exit()
		
	def loadParamsFromCam(self):
		if self.cam.getParamsFromCAM():
			self.builder.get_object("width").set_value(self.cam.getWidth())
			self.builder.get_object("height").set_value(self.cam.getHeight())
			self.builder.get_object("fps").set_value(self.cam.getFPS())
			self.builder.get_object("quality").set_value(self.cam.getQuality())
			self.builder.get_object("exposure").set_value(self.cam.getExposure())
			self.builder.get_object("blacklevel").set_value(self.cam.getBlacklevel())			
			self.builder.get_object("gamma").set_value(self.cam.getGamma())
			self.builder.get_object("gain").set_value(self.cam.getGain())
			self.builder.get_object("saturation_red").set_value(self.cam.getSaturationRed())
			self.builder.get_object("saturation_blue").set_value(self.cam.getSaturationBlue())
			self.builder.get_object("RG_level").set_value(self.cam.getRGLevel())
			self.builder.get_object("BG_level").set_value(self.cam.getBGLevel())
			self.builder.get_object("autoexposure").set_active(self.cam.getAutoExposureStatus())
			self.builder.get_object("multicast").set_active(self.cam.getMulticastStatus())
			self.builder.get_object("photofinish").set_active(self.cam.getPhotoFinishState())
			self.builder.get_object("normal").set_active(not self.cam.getPhotoFinishState())

			# elphel 353:
			self.builder.get_object("trigger").set_active(self.cam.getTrigger())
			self.builder.get_object("flipH").set_active(self.cam.getFlipH())
			self.builder.get_object("flipH").set_active(self.cam.getFlipV())			

			if not self.cam.getAutoExposureStatus():
				self.builder.get_object("exposure").set_flags(gtk.SENSITIVE)

			self.setStreamerLabel()		
		

	def updateParams(self):
		if self.cam.getParamsFromCAM():
			self.updateStatus()
		else:
			self.builder.get_object("statusbar").push(0,"offline");
		self.update_id = gobject.timeout_add(1000, self.updateParams)				

	def load_state(self):
		if os.path.isfile(self.state_file):
			f = open(self.state_file, 'r')
			self.state = cPickle.load(f)
			f.close
		else:
			self.logger.debug("no state file found")
			self.state = {
				"trigger":0,
				"fps":25, "quality":95,
				"width":1920, "height":1080,
				"exposure":100,
				"autoexposure":1,				
				"flipH":0,
				"flipV":0,
				"gain":0,
				"gamma":0.5,
				"streamer":1,
				"white_balance":1
				}

		for k in self.state:
			if hasattr( self.builder.get_object(k) ,"set_value" ):
				self.builder.get_object(k).set_value(self.state[k])
			elif hasattr( self.builder.get_object(k) ,"set_active" ):
				self.builder.get_object(k).set_active(self.state[k])

		if self.state["autoexposure"] == 0:
			self.builder.get_object("exposure").set_flags(gtk.SENSITIVE)
			
		# intial data
		#self.builder.get_object("fps").set_value(fps)
		#self.builder.get_object("width").set_value(width)
		#self.builder.get_object("height").set_value(height)

	def save_state(self):
		self.state["width"] = self.builder.get_object("width").get_value()
		self.state["height"] = self.builder.get_object("height").get_value()
		self.state["fps"] = self.builder.get_object("fps").get_value()
		self.state["quality"] = self.builder.get_object("quality").get_value()
		self.state["exposure"] = self.builder.get_object("exposure").get_value()
		self.state["blacklevel"] = self.builder.get_object("blacklevel").get_value()			
		self.state["gamma"] = self.builder.get_object("gamma").get_value()
		self.state["gain"] = self.builder.get_object("gain").get_value()
		self.state["saturation_red"] = self.builder.get_object("saturation_red").get_value()
		self.state["saturation_blue"] = self.builder.get_object("saturation_blue").get_value()
		self.state["RG_level"] = self.builder.get_object("RG_level").get_value()
		self.state["BG_level"] = self.builder.get_object("BG_level").get_value()
		self.state["autoexposure"] = self.builder.get_object("autoexposure").get_active()
		self.state["multicast"] = self.builder.get_object("multicast").get_active()
		self.state["photofinish"] = self.builder.get_object("photofinish").get_active()

		# elphel 353:
		self.state["trigger"] = self.builder.get_object("trigger").get_active()
		self.state["flipH"] = self.builder.get_object("flipH").get_active()
		self.state["flipV"] = self.builder.get_object("flipV").get_active()

		self.logger.debug("saving state")
		f = open(self.state_file, 'w')
		cPickle.dump(self.state,f)
		f.close
		return True		
		
	def on_window_delete_event(self, widget, event, data=None):	
		# If you return FALSE in the "delete_event" signal handler,
		# GTK will emit the "destroy" signal. Returning TRUE means
		# you don't want the window to be destroyed.
		# This is useful for popping up 'are you sure you want to quit?'
		# type dialogs.
		return False
	
	def on_window_destroy(self, widget, data=None):
		print "window destroy"
		gtk.main_quit()
		
	def on_quit_activate(self, widget, data=None):
		print "quit"
		gtk.main_quit()					
		
	def on_width_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set WIDTH: %f" % val)

			if hasattr(self, "player"):
				self.gst_stop_pipeline()

			self.cam.setWidth(val)
			self.save_state()
		
			if hasattr(self, "player"):
				self.gst_start_pipeline()

	def on_height_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()	
			self.logger.debug("set HEIGHT: %f" % val)

			if hasattr(self, "player"):
				self.gst_stop_pipeline()

			self.cam.setHeight(val)	
			self.save_state()
		
			if hasattr(self, "player"):
				self.gst_start_pipeline()			
		

	def on_fps_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set FPS: %f" % val)
			self.cam.setFPS(val)	
			self.save_state()

	def on_trigger_toggled(self, obj):		
		if self.controls_active:
			if obj.get_active():	
				self.fps_by_trigger = True
			else:
				self.fps_by_trigger = False
			self.cam.setTrigger(self.fps_by_trigger)
			self.save_state()			
		
	def on_quality_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set JPEG Quality: %f" % val)
			self.cam.setQuality(val)
			self.save_state()

	def on_gain_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set gain to : %f" % val)
			self.cam.setGain(val)
			self.save_state()

	def on_blacklevel_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set blacklevel to : %f" % val)
			self.cam.setBlacklevel(val)
			self.save_state()		

	def on_gamma_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set gamma to : %f" % val)
			self.cam.setGamma(val)
			self.save_state()		
		
	def on_autoexposure_toggled(self, obj):		
		if self.controls_active:
			if obj.get_active():	
				self.builder.get_object("exposure").unset_flags(gtk.SENSITIVE)
				self.logger.debug("set autoexposure on")
				self.cam.setAutoExposureOn()
			else:
				self.builder.get_object("exposure").set_flags(gtk.SENSITIVE)
				self.logger.debug("set autoexposure off")
				self.cam.setAutoExposureOff()
			self.save_state()
		
	def on_exposure_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set EXPOSURE: %f" % val)
			self.cam.setExposure(val)
			self.save_state()
		
	def on_preview_toggled(self, obj):			
		if self.controls_active:
			if obj.get_active():	
				self.gst_preview_on()
				self.logger.debug("preview on")	
			else:
				self.gst_preview_off()
				self.logger.debug("preview off")	

	def on_auto_white_balance_toggled(self, obj):		
		if self.controls_active:
			if obj.get_active():	
				#self.builder.get_object("white_balance").unset_flags(gtk.SENSITIVE)
				self.logger.debug("set auto white balance on")
				self.cam.setAutoWhiteBalanceOn()
			else:
				#self.builder.get_object("exposure").set_flags(gtk.SENSITIVE)
				self.logger.debug("set auto white balance off")
				self.cam.setAutoWhiteBalanceOff()
			self.save_state()

	def on_white_balance_clicked(self, obj):		
		if self.controls_active:
			self.cam.setAutoWhiteBalance()
			self.builder.get_object("RG_level").set_value(self.cam.getRGLevel())
			self.builder.get_object("BG_level").set_value(self.cam.getBGLevel())			
			self.logger.debug("trigger white balance")

	def on_saturation_red_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set csr to : %f" % val)
			self.cam.setSaturationRed(val)

	def on_saturation_blue_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set csb to : %f" % val)
			self.cam.setSaturationBlue(val)

	def on_BG_level_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set bscale to : %f" % val)
			self.cam.setBGLevel(val)

	def on_RG_level_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set rscale to : %f" % val)
			self.cam.setRGLevel(val)		
			
	def on_streamer_clocked(self, obj):		
		if self.controls_active:
			if obj.get_active():	
				self.logger.debug("set streamer on")
				self.cam.startStream()
			else:
				self.logger.debug("set streamer off")
				self.cam.stopStream()
			self.save_state()

	def on_multicast_toggled(self, obj):		
		if self.controls_active:
			if obj.get_active():	
				self.logger.debug("set streamer to multicast")
				self.cam.streamMulticast()
			else:
				self.logger.debug("set streamer to unicast")
				self.cam.streamUnicast()
			self.state['multicast'] = obj.get_active()
			self.save_state()

	def on_flipV_toggled(self, obj):
		if self.controls_active:
			self.logger.debug("set flipV to:" + str(obj.get_active()))
			self.cam.setFlipV(obj.get_active())
			self.state['flipV'] = obj.get_active()
			self.save_state()					

	def on_flipH_toggled(self, obj):
		if self.controls_active:
			self.logger.debug("set flipH to:" + str(obj.get_active()))
			self.cam.setFlipH(obj.get_active())
			self.save_state()

	def on_reboot_clicked(self, obj):
		if self.controls_active:
			self.cam.rebootCam()

	def on_photofinish_clicked(self, obj):
		if self.controls_active:
			self.cam.startPhotofinish()

	def on_normal_clicked(self, obj):
		if self.controls_active:
			self.cam.startNormalMode()

	def on_streamer_clicked(self, obj):		
		if self.controls_active:
			if self.cam.getStreamerStatus():	
				self.logger.debug("set streamer off")
				self.cam.stopStream()
			else:
				self.logger.debug("set streamer on")
				self.cam.startStream()
		self.updateStatus()

	## preview functions

	def update_image(self):
		#self.rawImg = 
		self.pixbufLoader = gtk.gdk.PixbufLoader()
		self.pixbufLoader.write(urllib.urlopen(self.img_src).read())
		self.pixbuf = self.pixbufLoader.get_pixbuf()
		self.pixbuf = self.pixbuf.scale_simple(
			self.width, self.pixbuf.get_height() * self.width/self.pixbuf.get_width(), 
			gtk.gdk.INTERP_BILINEAR)
		#self.image = gtk.image_new_from_pixbuf(self.pixbuf)
		self.image.set_from_pixbuf(self.pixbuf)
		self.pixbufLoader.close()	
		
		# returning True repeats this timeout callback
		return True

	def setup_pipeline(self):
		proto = "protocols=0x00000001"
		if self.cam.getMulticastStatus:
			proto = "protocols=0x00000002"
		self.pipeline = "rtspsrc location=%s latency=100 %s ! rtpjpegdepay ! jpegdec ! xvimagesink" % (self.videosrc, proto)
		
	def gst_launch(self):
		# Set up the gstreamer pipeline
		self.player = gst.parse_launch (self.pipeline)
		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.enable_sync_message_emission()
		bus.connect("message", self.on_message)
		bus.connect("sync-message::element", self.on_sync_message)	
	
	def gst_stop_pipeline(self):		
		self.logger.debug(self.player.get_state())
		self.player.set_state(gst.STATE_PAUSED)
		self.logger.debug(self.player.get_state())
		self.player.set_state(gst.STATE_READY)
		self.logger.debug(self.player.get_state())
		self.player.set_state(gst.STATE_NULL)
		self.logger.debug(self.player.get_state())
					
	def gst_start_pipeline(self):	
		self.gst_launch()
		self.player.set_state(gst.STATE_READY)
		self.logger.debug(self.player.get_state())
		self.player.set_state(gst.STATE_PAUSED)
		self.logger.debug(self.player.get_state())
		self.player.set_state(gst.STATE_PLAYING)
		self.logger.debug(self.player.get_state())	
			
	def gst_preview_on(self):
		self.preview_window.show()
		self.gst_start_pipeline()
	
	def gst_preview_off(self):		
		self.gst_stop_pipeline()
		self.preview_window.hide()			
			
	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
		elif t == gst.MESSAGE_ERROR:
			err, debug = message.parse_error()
			self.logger.error("Error: %s" % err, debug)
			self.player.set_state(gst.STATE_NULL)

	def on_sync_message(self, bus, message):
		if message.structure is None:
			return
		message_name = message.structure.get_name()
		if message_name == "prepare-xwindow-id":
			# Assign the viewport
			imagesink = message.src
			imagesink.set_property("force-aspect-ratio", True)
			imagesink.set_xwindow_id(self.movie.window.xid)

	def setStreamerLabel(self):
		if self.cam.getStreamerStatus():
			self.builder.get_object("streamer").set_label("Stop Streamer")
		else:
			self.builder.get_object("streamer").set_label("Start Streamer")				

	def updateStatus(self):
		if self.cam.getAutoExposureStatus():
			self.controls_active = False
			self.builder.get_object("exposure").set_value(self.cam.getExposure())
			self.controls_active = True

		self.setStreamerLabel()
			
		if self.cam.getStreamerStatus():
			str = "streaming"
		else:
			str = "no stream"

		str = str + " (Sensor state: " + self.cam.getSensorState() + ")"
		
		if self.cam.getPhotoFinishState():
			str = str + " - PHOTOFINSH"
		else:
			str = str + " - NORMAL"

		str = "%s / FPS: %3.f" %(str, self.cam.getFPS())
		
		self.builder.get_object("statusbar").push(0,str);

		self.controls_active = False
		self.builder.get_object("photofinish").set_active(self.cam.getPhotoFinishState())
		self.builder.get_object("normal").set_active(not self.cam.getPhotoFinishState())		
		self.controls_active = True
		
	def main(self):
		gtk.gdk.threads_init()
		gtk.main()
		
		

if __name__ == '__main__':
	camcontrol = CamControl("192.168.0.10")
	camcontrol.main()
