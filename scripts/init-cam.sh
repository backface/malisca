#!/bin/sh

CAM=192.168.0.9

if [ "$1" = "jp4" ]; then
	wget -q -O /dev/null "http://$CAM/setparams.php?COLOR=2"
else
	wget -q -O /dev/null "http://$CAM/setparams.php?COLOR=1"
fi

wget -q -O /dev/null "http://$CAM/camvc.php?set=0/gg:1.0/ggb:1.0/" 
wget -q -O /dev/null "http://$CAM/setparams.php?WOI_HEIGHT=48&WOI_TOP=948&QUALITY=95"  
wget -q -O /dev/null "http://$CAM/setparams.php?AUTOEXP_ON=0&WB_EN=0"  
wget -q -O /dev/null "http://$CAM/setparams.php?FPSFLAGS=2&TRIG_PERIOD=960000.000000&FP1000SLIM=200000.000000"
wget -q -O /dev/null "http://$CAM/setparams.php?TRIG=4"
wget -q -O /dev/null "http://$CAM/setparams.php?QUALITY=96"

#sleep 1
#wget -O /dev/null "http://$CAM/setparams.php?DAEMON_EN_STREAMER=1"
# init camogm
#wget -O /dev/null "http://192.168.0.10/camogmgui/camogm_interface.php?cmd=run_camogm"


