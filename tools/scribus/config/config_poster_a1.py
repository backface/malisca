######################################
# -*- coding: utf-8 -*

from scribus import *

class Config:

	imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-04-27--westautobahn-II/1440x320/"
	#imagepath = "/data/projects/A1/tiles/2011-04-27--westautobahn-I/512x512"
	imagepath = "/data/projects/A1/selection/512x512/"
	#imagepath = "/data/projects/A1/Ein-Stueck-A1/512x512/"
	
	offset = 1
	limit = 0
	#limit = 1013
	limit = 966
	
	readLogs = True
	logstyle = "new"

	page_size = PAPER_A0
	orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
	units = UNIT_POINTS

	footer = "Copyright © Michael Aschauer, 2011"
	title = "A1 Westautobahn"

	margin = 14.2
	margin_fac = 0.35




