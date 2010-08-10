#!/bin/bash

#init_1='/admin-bin/ccam.cgi?opt=vhcxyu+!-&dh=2&dv=2&ww=4000&wh=4000&bh=1&bv=1&iq=70&sens=2&bit=8&gam=64&pxl=10&csb=200&csr=200&e=100&wl=0&wt=0'
#init_2='/admin-bin/ccam.cgi?opt=vhcxy-+&rscale=auto&bscale=auto'

MENCODER=/usr/local/src/mplayer/mencoder
MPLAYER=mplayer

CAM_URL="http://192.168.0.9"
PFH=2
WIDTH=2048
HEIGHT=96
FPS=512

DATE=$(date --utc +%Y%m%d)
let CROP_H=$HEIGT-2
let TOP=(1536-$HEIGHT)/2
echo CROP: $CROP_H px
echo TOP: $TOP px

INIT_STRING="$CAM_URL/admin-bin/ccam.cgi?opt=vhcxmuy+!$URL&pfh=$PFH&ww=$WIDTH&wh=$HEIGHT&wt=$TOP&fps=$FPS&dh=1&dv=1"

STREAMER_START_URL="$CAM_URL/sctl.cgi?cmd=start&transport=mcast&addr=232.0.0.1&port=20000"
STREAMER_STOP_URL="$CAM_URL/sctl.cgi?cmd=stop"

#init cam


echo "init camera [$INIT_STRING]"

wget -q -O /dev/null $STREAMER_STOP_URL
sleep 1

wget -q -O /dev/null $INIT_STRING
sleep 1

echo "starting streamer [$STREAMER_START_URL]"
wget -q -O /dev/null $STREAMER_START_URL

sleep 1

mplayer -nocache rtsp://192.168.0.9:554


