
CC = g++
CFLAGS= -g -O2 -lgps
CINCLUDE=
LINUXLDFLAGS=
OPENCV_FLAGS=$(shell pkg-config opencv --cflags --libs)
GSTREAMER_FLAGS=$(shell pkg-config --cflags --libs gstreamer-plugins-base-0.10 gstreamer-0.10)
GL_FLAGS=$(shell pkg-config --cflags --libs gl) -lGLU -lglut


SOURCES=straighten.cpp
TARGETS=straighten

all: $(TARGETS)

%:%.cpp
	$(CC) $(CFLAGS) $(OPENCV_FLAGS) $@.cpp -o $@
	
install:
	cp linescan /usr/local/bin
	
clean:
	rm $(TARGETS)
		
