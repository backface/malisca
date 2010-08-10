#!/bin/bash

mplayer -nocache rtsp://192.168.0.9:554 -vo jpeg:outdir=scan-data:quality=100
