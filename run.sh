#!/bin/bash

#a simple startup script, just to show/note some necessary preparations

#stop unwanted services
sudo service apache2 stop
sudo service nmbd stop
sudo service bluetooth stop
sudo service cups stop
sudo service network-manager stop
sudo /etc/init.d/networking restart
sudo ifup eth0

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

if [ "$1" = "jp4" ]; then
	./scripts/init-cam.sh jp4
else
	./scripts/init-cam.sh
fi

# now run linescanner

while [ 1 == 1 ]; do

	#wget -q -O /dev/null http://192.168.0.10/camogmgui/camogm_interface.php?cmd=start

	if [ "$1" = "jp4" ]; then
		./linescan --pre --gps --jp4
	else
		./linescan --pre --gps
	fi

	#wget -q -O /dev/null http://192.168.0.10/camogmgui/camogm_interface.php?cmd=stop
	
done

