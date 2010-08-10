for k in jp4-*.avi; do

	FRAMES_DIR=frames--${k%.avi}
	TILE_DIR=tiles--${k%.avi}
	TIFF_DIR=frames_processed--${k%.avi}

	mkdir $FRAMES_DIR
	mkdir $TILE_DIR
	mkdir $TIFF_DIR

	echo "processing movie to frames .."
	ffmpeg i $k -vcodec copy $FRAMES_DIR/frame-%05d.jpg

	echo "make DNG from jpg46 .."
	cd $FRAMES_DIR
	for i in *.jpg; do
		echo "make DNG from jpg46: ${i%jpg}dng"
		elphel_dng 100 $i ../$TIFF_DIR/${i%jpg}dng
	done;
	cd ..

	echo "rotate and make tiff and jpeg"
	cd $TIFF_DIR
	for i in *.dng; do
		echo "make tiff from DNG: ${i%dng}tiff"
		dcraw -W -a -4 -T -q 3 $i
		echo "rotate to: ${i%dng}jpg"
		convert ${i%dng}tiff -rotate -90 -quality 100 ${i%dng}jpg
	done;
	cd ..

	echo "render tiles .."
	makedunavtiles.py -s 2592x2592 -i $TIFF_DIR/\*.jpg -o $TILE_DIR/tile.jpg
	rm -rf $FRAMES_DIR;

done

