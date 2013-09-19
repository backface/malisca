
CC = gcc
LINUXCFLAGS= -O3 -lgps -Wall
LINUXINCLUDE=
LINUXLDFLAGS=
OPENCV_FLAGS=$(shell pkg-config opencv --cflags --libs)
GSTREAMER_FLAGS=$(shell pkg-config --cflags --libs gstreamer-plugins-base-0.10 gstreamer-0.10) -lgstapp-0.10
GL_FLAGS=$(shell pkg-config --cflags --libs gl) -lGLU -lglut


SOURCES=$(sort $(filter %.c, $(wildcard *.c */*.c)))
TARGETS = $(SOURCES:.c=)

all: $(TARGETS)

%:%.c
	$(CC) $(LINUXCFLAGS) $(GSTREAMER_FLAGS) $(OPENCV_FLAGS)  $(GL_FLAGS)  $@.c -o $@
	
install:
	cp linescan /usr/local/bin
	
clean:
	rm $(TARGETS)
		
