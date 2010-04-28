#!/bin/bash

# necessary due to strange bug in gst_init() with LANG=de_AT.UTF-8
export LANG=C

GPSD_PID=$(pidof gpsd)
GPSD_CMD="/usr/local/sbin/gpsd /dev/ttyUSB0"

if [ "$GPSD_PID" == "" ]; then
	echo "no gpsd.. trying to start it"
	$GPSD_CMD
else
	echo "gpsd is running"
fi

./linescan --gps

