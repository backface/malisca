#!/bin/bash

for k in *-??????.avi; do

	OUT=output
	mkdir $OUT
	mkdir $OUT/normal/
	
	FRAMES_DIR=$OUT/normal/frames--${k%.avi}
	TILES_DIR=$OUT/normal/
	mkdir $FRAMES_DIR
	mkdir $TILES_DIR

	echo "processing movie to frames .."
	ffmpeg -i $k -vcodec copy $FRAMES_DIR/frame-%05d.jpg

	echo "rotate frames .."
	
	for i in $FRAMES_DIR/frame*.jpg; do
		echo "rotate to: $i"
		convert $i -rotate -90 ${i%.jpg}.ppm
	done 	

	echo "render tiles .."
	#makedunavtiles-c.py -s 2048x2048 -i $FRAMES_DIR/\*.jpg -o $TILES_DIR/${k%.avi}-tile.jpg
	makedunavtiles-c.py -s 10368x2592 -i $FRAMES_DIR/\*.ppm -o $TILES_DIR/${k%.avi}-tile.jpg
	
	rm -rf $FRAMES_DIR
	
done;
