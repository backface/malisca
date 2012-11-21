######################################
# -*- coding: utf-8 -*

from scribus import *

#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-04-18--krems-linz/128x128"
#imagepath = "/home/mash/data/projects/rivers-as-lines/satlisca/scan-data/ganges/20.0m/12/landsat/512"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-06-17--linz-krems/512x512"
#imagepath = "/data/projects/rivers-as-lines/satlisca/scan-data/nile-via-damietta/20m/12/landsat/512/"
#imagepath = "/data/projects/rivers-as-lines/satlisca/scan-data/danube-via-sulina+breg/20m/12/landsat/512/"
#imagepath = "/data/projects/donau//scan-data/2006-04-17--pwc-asten-wien/"
#imagepath = "/data/projects/donau//scan-data/2005-07-23--pwc-almasfuszito-hainburg/"
#imagepath = "/data/projects/slitscan/malisca/tile-data/2011-04-27--westautobahn-Ib/320x320/"
#imagepath = "/data/projects/slitscan/old/pd-slitscanner/scan-data/2011-04-18--krems-linz/"

if False:
	imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-13--varanasi-deshaked/2592x2592-bg_white"
	offset = 0
	limit = 194
	readLogs = True
	logstyle = "new"
	page_size = PAPER_A2
	orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
	footer = "Copyright © Michael Aschauer, 2011"
	title = "A CHEAP LOW-QUALITY SAMPLE: Along The Ghats of Varanasi/Banaras - The Forest of Bliss"

if True:
	imagepath  = "/data/projects/slitscan/malisca/tile-data/2012-01-08--guwahati-north-deshaked/2592x2592"
	offset = 0
	limit = 0
	readLogs = True
	logstyle = "new"
	page_size = PAPER_A2
	orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
	footer = "Copyright © Michael Aschauer, 2012"
	title = "North Guwahati (Sample)"
	
# VARANASI recording
#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi-deshaked/2592x2592-level/"
#offset = 34
#limit = 177
#readLogs = False
#page_size = PAPER_A1
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#footer = "Copyright © Michael Aschauer, http://m.ash.to, 2011"
#title = "Along The Ghats of Benaras - The Forest of Bliss"

# EASTERN SIDE
#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi/2592x2592/"
#offset = 224
#limit = 0
#readLogs = False
#page_size = PAPER_A2
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#footer = "Copyright © Michael Aschauer, 2011"

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi-deshaked/2536x2536/"
#offset = 224
#limit = 0
#readLogs = False
#page_size = PAPER_A2
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#footer = "Copyright © Michael Aschauer, 2011"

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-06--varanasi/2592x2592/"
#offset = 25
#limit = 178

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-15--banares-chunar/128/"
#offset = 37
#limit = 0

#imagepath  = "/data/projects/slitscan/malisca/tile-data/2011-12-16--chunar-banares/128/"
#offset = 2
#limit = 180
#readLogs = False
#page_size = PAPER_A4


#footer = "Danube Panorama Project - http://danubepanorama.net  ·  Copyright © Michael Aschauer, 2011"
#footer = "Copyright © Michael Aschauer, 2011"
#footer = ""

#title = "Komarom (HU) - Hainburg (AT)"
#title = "Weissenkirchen (AT) - Linz (AT)"
#title = "Linz (AT) - Krems (AT)"
#title = "WHAT IF YOU WOULD PULL NILE TO A STRAIGHT LINE?  ·  The Nile from its tributaries Nyabarong and  Kagera (Rwanda) to the Mediterrian Sea via the Damietta branch"
#title = "WHAT IF YOU WOULD PULL GANGES TO A STRAIGHT LINE?"
#title = ""

#page_size = PAPER_A2
#page_size = (600,900)
#units = UNIT_MILLIMETERS
#orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
#margin = 5


units = UNIT_POINTS
orientation = LANDSCAPE # LANDSCAPE, PORTRAIT
margin = 14.2
margin_fac = 0.33



