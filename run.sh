#!/bin/bash

#a simple startup script, just to show/note some necessary preparations

#stop unwanted services
sudo service apache2 stop
sudo service nmbd stop
sudo service bluetooth stop
sudo service cups stop

# necessary due to strange bug in gst_init() with LANG=de_AT.UTF-8
export LANG=C

# setup route for multicast
sudo route add -net 232.0.0.0 netmask 255.0.0.0 dev eth0

#start gpsd - if not runing
GPSD_PID=$(pidof gpsd)
GPSD_CMD="/usr/local/sbin/gpsd /dev/ttyUSB0"

if [ "$GPSD_PID" == "" ]; then
	echo "no gpsd.. trying to start it"
	$GPSD_CMD
else
	echo "gpsd is running"
fi

./scripts/init-cam.sh

# now run linescanner
while [ 1 == 1 ]; do
	./linescan --pre --gps
done

