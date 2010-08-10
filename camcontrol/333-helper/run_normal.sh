#!/bin/sh
# start and watch stream from elphel333

MENCODER=mencoder
MPLAYER=mplayer

CAM_URL="http://192.168.0.9"
PFH=0
WIDTH=1920
HEIGHT=1536
FPS=15

INIT_STRING="$CAM_URL/admin-bin/ccam.cgi?opt=vhcxyu+!-&pfh=$PFH&ww=$WIDTH&wh=$HEIGHT&fps=$FPS&dh=1&dv=1&iq=90&wt=$WT&wl=$WL"

#STREAMER_START_URL="http://192.168.0.9/sctl.cgi?cmd=stop&transport=mcast&addr=232.0.0.1&port=20000&fps=$FPS"
STREAMER_STOP_URL="$CAM_URL/sctl.cgi?cmd=stop"
STREAMER_START_URL="$CAM_URL/sctl.cgi?cmd=start&transport=mcast&addr=232.0.0.1&port=20000"
STREAMER_STOP_URL="$CAM_URL/sctl.cgi?cmd=stop"

#init cam


echo "init camera [$INIT_STRING]"
wget -q -O /dev/null $STREAMER_STOP_URL
sleep 1
wget -q -O /dev/null $INIT_STRING
sleep 2
echo "starting streamer [$STREAMER_START_URL]"
wget -q -O /dev/null $STREAMER_START_URL
sleep 2

echo "starting player"
$MPLAYER -nocache rtsp://192.168.0.9:554 -nosound

