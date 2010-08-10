#!/bin/bash

for k in *.avi; do

	FRAMES_DIR=frames--${k%.avi}
	TILES_DIR=tiles--${k%.avi}
	mkdir $FRAMES_DIR
	mkdir $TILES_DIR

	echo "processing movie to frames .."
	ffmpeg -i $k -vcodec copy $FRAMES_DIR/frame-%05d.jpg

	echo "rotate frames .."
	
	for i in $FRAMES_DIR/frame*.jpg; do
		echo "rotate to: $i"
		convert $i -rotate -90 -quality 100 $i
	done

	echo "render tiles .."
	makedunavtiles-c.py -s 2048x2048 -i $FRAMES_DIR/\*.jpg -o $TILES_DIR/tile.jpg
	rm -rf $FRAMES_DIR
	
done;
