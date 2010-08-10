#!/bin/sh

CAM=192.168.0.10

wget -O /dev/null "http://$CAM/setparams.php?DAEMON_EN_STREAMER=0"
wget -O /dev/null "http://$CAM/camvc.php?set=0/gg:1.0/ggb:1.0/"
wget -O /dev/null "http://$CAM/setparams.php?WOI_HEIGHT=96&WOI_TOP=924&QUALITY=100"
wget -O /dev/null "http://$CAM/setparams.php?AUTOEXP_ON=0&WB_EN=0"
wget -O /dev/null "http://$CAM/setparams.php?FPSFLAGS=2&TRIG_PERIOD=960000.000000&FP1000SLIM=200000.000000"
wget -O /dev/null "http://$CAM/setparams.php?TRIG=4"
wget -O /dev/null "http://$CAM/setparams.php?PF_HEIGHT=2"

sleep 1

wget -O /dev/null "http://$CAM/setparams.php?DAEMON_EN_STREAMER=1"
