######################################
# -*- coding: utf-8 -*

from scribus import *

class Config:

	imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-04-27--westautobahn-II/1440x320/"
	offset = 0
	limit = 0
	
	readLogs = False
	logstyle = "new"

	page_size = PAPER_A0
	orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
	units = UNIT_POINTS

	footer = "Copyright © Michael Aschauer, 2011"
	title = "A1 Westautobahn"

	margin = 14.2
	margin_fac = 0.33




