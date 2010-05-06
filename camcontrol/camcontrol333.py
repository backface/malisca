#!/usr/bin/python 

import sys, os
import pygtk, gtk, gobject
import urllib
import gst
import logging
import cPickle
import glib

from camera.elphel333 import Camera


class CamControl:
		
	def __init__(self,ip):
		self.controls_active = False
		self.ip = ip
		self.img_src = "http://%s/admin-bin/ccam.cgi?opt=vhcxym" % self.ip
		self.video_src = "rtsp://%s:554" % self.ip		
		self.state_file = "camcontrol333.state"
		self.fps_by_trigger = False

		logging.basicConfig(level=logging.WARNING)	
		self.logger = logging.getLogger('camcontrol GUI')		

		self.builder = gtk.Builder()
		self.loadGUI("camcontrol333.xml")			
		self.builder.connect_signals(self)
        
		self.window = self.builder.get_object("window")
		self.window.show()				
		self.preview_window = self.builder.get_object("preview_win")
		self.builder.get_object("statusbar").push(0,"--");					
		self.cam = Camera(ip)

		# for 333
		self.loadParamsFromCam()
		self.controls_active = True
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
		if self.cam.getParamsFromCAM() and self.cam.getExposureParamsFromCAM():
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
			#self.builder.get_object("whitelevel").set_value(self.cam.getWhitelevel())
			#self.builder.get_object("streamer").set_active(self.cam.getStreamerStatus())

			if not self.cam.getAutoExposureStatus():
				self.builder.get_object("exposure").set_flags(gtk.SENSITIVE)

			self.setStreamerLabel()

	def updateParams(self):
		if self.cam.getParamsFromCAM():
			self.updateStatus()
		else:
			self.builder.get_object("statusbar").push(0,"offline");
		self.update_id = gobject.timeout_add(1000, self.updateParams)			
		
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
			self.cam.setWidth(val)

	def on_pf_height_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set WIDTH: %f" % val)
			self.cam.setWidth(val)			
		
	def on_height_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()	
			self.logger.debug("set HEIGHT: %f" % val)
			self.cam.setHeight(val)	

	def on_fps_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set FPS: %f" % val)
			self.cam.setFPS(val)	

	def on_trigger_toggled(self, obj):		
		if self.controls_active:
			if obj.get_active():	
				self.fps_by_trigger = True
			else:
				self.fps_by_trigger = False
		#self.cam.setTrigger(self.fps_by_trigger)		
		
	def on_quality_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set JPEG Quality: %f" % val)
			self.cam.setQuality(val)

	def on_gain_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set gain to : %f" % val)
			self.cam.setGain(val)

	def on_blacklevel_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set blacklevel to : %f" % val)
			self.cam.setBlacklevel(val)

	def on_whitelevel_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set whitelevel to : %f" % val)
			self.cam.setWhitelevel(val)							

	def on_gamma_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set gamma to : %f" % val)
			self.cam.setGamma(val)

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

	def on_exposure_value_changed(self, obj):
		if self.controls_active:
			val = obj.get_value()
			self.logger.debug("set EXPOSURE: %f" % val)
			self.cam.setExposure(val)

	def on_white_balance_clicked(self, obj):		
		if self.controls_active:
				self.cam.setAutoWhiteBalance()
				self.builder.get_object("RG_level").set_value(self.cam.getRGLevel())
				self.builder.get_object("BG_level").set_value(self.cam.getBGLevel())
				
	def on_streamer_clicked(self, obj):		
		if self.controls_active:
			if self.cam.getStreamerStatus():	
				self.logger.debug("set streamer off")
				self.cam.stopStream()
			else:
				self.logger.debug("set streamer on")
				self.cam.startStream()
		updateStatus()

	def on_rifix_clicked(self, obj):		
		if self.controls_active:
			self.cam.requestImage()

	def on_multicast_toggled(self, obj):		
		if self.controls_active:
			if obj.get_active():	
				self.logger.debug("set streamer to multicast")
				self.cam.streamMulticast()
			else:
				self.logger.debug("set streamer to unicast")
				self.cam.streamUnicast()

	def on_photofinish_clicked(self, obj):
		if self.controls_active:
			self.cam.startPhotofinish()

	def on_normal_clicked(self, obj):
		if self.controls_active:
			self.cam.startNormalMode()

	def on_reboot_clicked(self, obj):
		os.system("./camera/reboot333")		


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

		
		
		
	def main(self):
		gtk.gdk.threads_init()
		gtk.main()

				

if __name__ == '__main__':
	camcontrol = CamControl("192.168.0.9")
	camcontrol.main()
