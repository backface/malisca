/*
 * MALISCA linescanner
 * ===============================
 *
 * with realtime preview
 * Copyright © 2010, Michael Aschauer <m@ash.to>
 * license: GPLv3 - see LICENSE or http://www.gnu.org/licenses/gpl-3.0.txt
*/

#include <time.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <pthread.h>
#include <signal.h>
#include <sys/prctl.h>
#include <locale.h>
#include <signal.h>

#include "highgui.h"
#include "cv.h"


CvVideoWriter *writer;
IplImage* buffer4gl, *flatframe, *darkframe;
IplImage* tilebuffer[100];
IplImage* frame_crop;
IplImage* tile_tmp;

pthread_mutex_t frame_mutex;
IplImage* frame;

pthread_mutex_t last_full_frame_mutex;
IplImage* last_full_frame;

pthread_t view_thread;
int view_thread_id;

#include <gst/gst.h>
#include <gst/app/gstappsink.h>

GstElement *sink, *pipeline;

#include <GL/glut.h>
#include <GL/gl.h>

#define IsRGB(s) ((s[0] == 'R') && (s[1] == 'G') && (s[2] == 'B'))
#define IsBGR(s) ((s[0] == 'B') && (s[1] == 'G') && (s[2] == 'R'))

#ifndef GL_CLAMP_TO_BORDER
#define GL_CLAMP_TO_BORDER 0x812D
#endif
#define GL_MIRROR_CLAMP_EXT 0x8742

void *font = GLUT_BITMAP_HELVETICA_12;
//void *font = GLUT_BITMAP_8_BY_13;
GLenum format;
GLuint texture[2];

int draw_line = 1;
int draw_zoom = 0;
int draw_grey = 0;

#include <sys/inotify.h>
#define I_EVENT_SIZE  ( sizeof (struct inotify_event) )
#define I_BUF_LEN     ( 1024 * ( I_EVENT_SIZE + 16 ) )

#include <sys/stat.h>
struct stat st;

#include <ctype.h>
#include <sys/types.h>
#include "gps.h"

struct gps_data_t *gpsdata;
struct gps_fix_t gpsfix;

char *gpsd_host;
char *gpsd_port;
char gps_status_str[255];

FILE *gpslog_file;
double distance=0;


char *conffile = "linescan.conf";
char *output_file;
char *watch_dir;
char *watch_src_cmd;
char *output_dir = "scan-data";

char *gst_pipeline;
char *gst_jp4pipeline;
char gst_default[255]  = "videotestsrc ! ffmpegcolorspace";
char str_info[255];
char str_gps[255];
char size_str[20];
char utc[255];

int scanline = 0;
int line_height = 2;
int buf_height = 32;
int quality = 99;
long framecount = 0;
long outframecount = 0;
int done = 0;
int tilenr, tile_width, tile_height;

int flag_dropframes = 0;
int flag_write_movie = 1;
int flag_write_images = 0;
int flag_verbose = 0;
int flag_display = 1;
int flag_gps = 0;
int flag_watcher_mode = 0;
int flag_prescanned=0;
int flag_downscale=1;
int flag_jp4 = 0;
int flag_calib = 0;

int waiting_eos = 0;

double fps;
double fps_time;
double t, tf, tt, t_total;
char max=0, max_b=0, max_r=0, max_g=0,min_b=0, min_g=0, min_r=0;

// structures for config file
struct confopt {
	const char *name;
	enum {
		co_int,
		co_bool,
		co_str,
	} type;
	union {
		int *pc_int;
		char **pc_str;
	};
};

struct confopt confopt[] = {
	{ "verbose", co_bool, { .pc_int = &flag_verbose } },
	{ "jp4out", co_bool, { .pc_int = &flag_jp4 } },
	{ "calib", co_bool, { .pc_int = &flag_calib } },
	{ "dropframes", co_int, { .pc_int = &flag_dropframes } },
	{ "bufferheight", co_int, { .pc_int = &buf_height } },
	{ "lineheight", co_int, { .pc_int = &line_height } },
	{ "quality", co_int, { .pc_int = &quality } },
	{ "gstpipeline", co_str, { .pc_str = &gst_pipeline } },
	{ "jp4pipeline", co_str, { .pc_str = &gst_jp4pipeline } },	
	{ "outfile", co_str, { .pc_str = &output_file } },
	{ "display", co_bool, { .pc_int = &flag_display } },
	{ "gps", co_bool, { .pc_int = &flag_gps } },
	{ "downscale", co_bool, { .pc_int = &flag_downscale } },
	{ "pre-scanned", co_bool, { .pc_int = &flag_prescanned } },
	{ "watch", co_bool, { .pc_int = &flag_watcher_mode } },
	{ "watch-dir", co_str, { .pc_str = &watch_dir } },
	{ "watch-src-cmd", co_str, { .pc_str = &watch_src_cmd } },
	{ NULL },
};

void mysignal_handler(int nr) {
	printf("\nIGNORE SIGSEGV!\n", nr);
}


// read config file
void read_config(void) {
	char line[255];
	char *n, *v;
	char f[255];
	FILE *c;
	int linenum = 0;
	struct confopt *conf;

	sprintf(f, "./%s", conffile);

	printf("trying to read config file: %s\n", f);
	c = fopen(f, "r");

	/* fall back to home and etc if config is not in local folder
	 * does not work - why?
	 */
	
	if (c == NULL) {
		sprintf(f, "~/.%s", conffile);
		printf("trying to read config file: %s\n", f);
		c = fopen(f, "r");
	}

	if (c == NULL) {
		sprintf(f, "/etc/%s", conffile);
		printf("trying to read config file: %s\n", f);
		c = fopen(f, "r");
	}
	
	if (c == NULL) {
		return;
	}	
		
	while (fgets(line, sizeof(line), c) != NULL) {		
		if (strchr(line, '\n') != NULL) {
			linenum++;
			*strchr(line, '\n') = 0;
		}
		if (strchr(line, '#') != NULL)
			*strchr(line, '#') = 0;
		for (n = line; isspace((unsigned char)*n); n++)
			;
		if (*n == 0)
			continue;
		for (v = n; !isspace((unsigned char)*v) && *v != 0; v++)
			;
		*v = 0;
		
		for (conf = confopt; conf->name != NULL; conf++)
			if (strcmp(conf->name, n) == 0)
				break;
		if (conf->name == NULL) {
			printf("%s:%d: option `%s' is not valid",
				conffile, linenum, n);
			exit(1);
		}
		for (v++; isspace((unsigned char)*v); v++)
			;
		if (*v == 0) {
			printf("%s:%d: option `%s' does not have a value",
				conffile, linenum, n);
			exit(1);
		}
		while (*v != 0 && isspace((unsigned char)v[strlen(v) - 1]))
			v[strlen(v) - 1] = 0;

		switch (conf->type) {
		case co_int:
			*conf->pc_int = atoi(v);
			break;
		case co_bool:
			if (strcmp(v, "yes") == 0 ||
			    strcmp(v, "true") == 0 ||
			    strcmp(v, "1") == 0)
				*conf->pc_int = 1;
			else if (strcmp(v, "no") == 0 ||
				 strcmp(v, "false") == 0 ||
				 strcmp(v, "0") == 0)
				*conf->pc_int = 0;
			else {
				printf("%s:%d: invalid boolean value",
					conffile, linenum, n);
				exit(1);
			}
			break;
		case co_str:
			
			if (*conf->pc_str != NULL)
				free(*conf->pc_str);
			*conf->pc_str = strdup(v);
			break;
		}
	}
		
	if (!gst_pipeline) 
		gst_pipeline = "videotestsrc ! ffmpegcolorspace";	
}

void read_options(int argc, char *argv[]) {
	int c;
	
	static struct option long_options[] = {
		/* These options set a flag. */
		{"verbose",		no_argument, &flag_verbose, 1},		
		{"brief",   	no_argument, &flag_verbose, 0},
		{"display", 	no_argument, &flag_display, 1},
		{"calib", 		no_argument, &flag_calib, 1},
		{"jp4", 		no_argument, &flag_jp4, 1},
		{"watch",	 	no_argument, &flag_watcher_mode, 1},
		{"nodisplay", 	no_argument, &flag_display, 0},
		{"nowrite", 	no_argument, &flag_write_movie, 0},
		{"pre",			no_argument, &flag_prescanned, 1},
		{"gps", 		no_argument, &flag_gps, 1},
		{"no-downscale",no_argument, &flag_downscale, 0},
		/* These options don't set a flag.
			We distinguish them by their indices. */
		{"output",  	required_argument, 0, 'o'},
		{"bufferheight",required_argument, 0, 'b'},
		{"lineheight",	required_argument, 0, 'l'},
		{"quality",	required_argument, 0, 'q'},
		{"watch-dir",	required_argument, 0, 'i'},
		{"test",	no_argument, 0, 't'},
		{0, 0, 0, 0}
	};
	
	while(1) {
		int option_index = 0;
    
		c = getopt_long (argc, argv,"o:b:l:ng:p:i:htvc:",long_options, &option_index);
		
		if (c == -1)
             break;
        
        switch(c) {
			
			case 0:
				break;
			
			case 'o':
				output_file = optarg;
				flag_write_movie = 1;
				flag_write_images = 0;
				break;
			
			case 'l':
				line_height = atoi(optarg);
				break;
				
			case 'b':
				buf_height = atoi(optarg);
				break;

			case 'q':
				quality = atoi(optarg);
				break;	

			case 'g':
				flag_gps = 1;				
				break;

			case 'v':
				flag_verbose = 1;				
				break;				

			case 'i':
				watch_dir = optarg;
				break;

			case 't':
				sprintf(gst_pipeline, "videotestsrc ! ffmpegcolorspace");
				break;
				
			case 'h':
				
			default:
				printf("Usage: linescan [options] file\n");
				printf("Options:\n");
				printf(" -o | --output FILE           Write result to video FILE.avi \n");
				printf("      --nowrite               Dont't write movie file \n");
				printf(" -l | --lineheight HEIGHT     height of scanline [px]\n");
				printf(" -b | --bufferheight HEIGHT   height of buffer image [px]\n");
				printf(" -q | --quality QUALITY       JPEG quality of video file (0-100)\n");
				printf(" -g | --gps                   log GPS data \n");				
				printf("      --verbose               be verbose \n");
				printf("      --jp4                   jp4 mode (Elphel raw)\n");
				printf("      --nodisplay             run without preview\n");
				printf("      --no-downscale(NOT YET) no downscale image for preview (slower and BROKEN!)\n");
				printf("      --calib (NOT YET!)      Use calibration (darkframe substraction and flatframe)\n");
				printf("      --watch                 watcher mode (use intofiy to watch a directory)\n");
				printf(" -i | --watch-dir             directory to watch\n");
				printf("      --watch-src-cmd         command to launch for watching mode\n");
				printf("      --pre                   source is already line-scanned\n");
				printf(" -h | --help                  print this help\n");
				exit(0);				
		}
	}	
}


void gps_process()
{
 // nothing
}

void gps_askfordata()
{
	while (gps_waiting(gpsdata)){
	    gps_poll(gpsdata);
	    
	    switch (gpsfix.mode) {
			case MODE_2D:
				//printf("2D FIX\n");
				sprintf(gps_status_str,"2d");
				break;
			case MODE_3D:
				//printf("3D FIX\n");
				sprintf(gps_status_str,"3d");
				break;
			default:
				//printf("NO FIX\n");
				sprintf(gps_status_str,"none");
				break;	
		}
	
		if (gpsdata->status > 0 && gpsfix.mode >=  MODE_2D) {
			distance += earth_distance(
				gpsfix.latitude, gpsfix.longitude,
				gpsdata->fix.latitude, gpsdata->fix.longitude);
		}		
		gpsfix = gpsdata->fix;
    }

}

void gps_setup()
{
	char logfilename[255];
	
	gpsd_host = "localhost";
	gpsd_port = "2947";
	
	if (gpsd_port == NULL) sprintf(gpsd_port,"%d",2947);
	if (gpsd_host == NULL) sprintf(gpsd_host,"%s","127.0.0.1");

	gpsdata = gps_open(gpsd_host, gpsd_port);
    if (!gpsdata) {
		fprintf(stderr,
		"no gpsd running or network error: %d, %s\n (%s:%s)\n",
		 errno, gps_errstr(errno), gpsd_host, gpsd_port);
		 flag_gps = 0;	 
    }
    else {
		//gps_set_raw_hook(gpsdata, gps_process);
		gps_stream(gpsdata, WATCH_ENABLE|WATCH_NEWSTYLE, NULL);
		
		if (flag_jp4) {
			sprintf(logfilename, "%s-jp4.avi.log",strtok(output_file,"."));
		}
		else {
			sprintf(logfilename, "%s.log",output_file);
		}
			
		gpslog_file = fopen(logfilename,"w");
		if (!gpslog_file) {
			fprintf(stderr,
			"could not open gps-logfile: %s",
			logfilename);
		}
		else {
			fprintf(gpslog_file,"#frame/tile; UTC; mode; \
latitude; longitude; altitude; \
speed; distance; track; climb; epx; epy; epv; \
satellites_visible; satellites_used\n");
		}
	}
    gps_clear_fix(&gpsfix); 
}

void gps_log()
{
	char utc[255];
	unix_to_iso8601(gpsdata->fix.time, utc, sizeof(utc));
	
	if (gpslog_file && gpsfix.mode >= MODE_2D && isnan(gpsfix.latitude)==0) {
		//if ( (gpsfix.mode >= MODE_2D) && (isnan(gpsfix.latitude)==0) ) {
			fprintf(gpslog_file,"%ld; %s; %s; %f; %f; %f; %f; %f; %f; %f; %f; %f; %f; %d; %d\n",
				outframecount,
				utc,
				gps_status_str,
				gpsfix.latitude,
				gpsfix.longitude,
				gpsfix.altitude,
				gpsfix.speed * MPS_TO_KPH,
				distance / 1000,
				gpsfix.track,
				gpsfix.climb,
				gpsfix.epx,
				gpsfix.epy,
				gpsfix.epv,
				gpsdata->satellites_visible,
				gpsdata->satellites_used);
		//}
	}
}


	
void gl_init() 
{
	// create buffer image
	if (flag_downscale)
		buffer4gl = cvCreateImage(cvSize(512, 512), 8, 3);
	else {
		buffer4gl = cvCreateImage(cvSize(frame->width, frame->width), 8, 3);

		int i;
		tilenr = frame->width / frame->height;
		tile_width = (buffer4gl->width );
		tile_height = (buffer4gl->height / tilenr);

		for(i = 0; i < tilenr; i++) {	
			tilebuffer[i] = cvCreateImage(cvSize(frame->width, frame->height), 8, 3);		
		}	
	}
	
	GLenum format = IsBGR(buffer4gl->channelSeq) ? GL_BGR_EXT : GL_RGBA;
	
	/* new */
	glLoadIdentity();
	glDisable(GL_CULL_FACE);
	glEnable(GL_BLEND);
	glEnable(GL_TEXTURE_2D);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glEnable (GL_DEPTH_TEST);
	glDepthFunc(GL_LEQUAL);
	  
	glGenTextures(1, &texture[0]);
	glBindTexture(GL_TEXTURE_2D, texture[0]);
	glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
	//GL_LINEAR is better looking than GL_NEAREST but seems slower..
	//glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	//glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
		buffer4gl->width, buffer4gl->height,
		0, format, GL_UNSIGNED_BYTE, buffer4gl->imageData);		
}

void gl_write(float x, float y, char *string) {
	int len, i;
	glColor4f(1.0, 1.0, 1.0, 1.0);
	glRasterPos2f(x, y);
	len = (int) strlen(string);
	for (i = 0; i < len; i++) {
		glutBitmapCharacter(font, string[i]);
	}
}

void gl_upload(IplImage *f)
{
	static char p_name[16];	
	if (!p_name)
		prctl(PR_GET_NAME,p_name);
		
	if (flag_verbose)
		g_print("thread %s: enter upload\n", 	p_name);
	
	double t = (double)cvGetTickCount();
	//printf("gl_upload frame");

	if (!f) {
		printf("could not load frame");
	}
	else {				
		int i;
		if (flag_downscale) {			
			if (!tile_tmp) {
				tilenr = f->width / f->height;
				tile_width = (buffer4gl->width );
				tile_height = (buffer4gl->height / tilenr);			
				tile_tmp = cvCreateImage( cvSize( tile_width, tile_height), 8, 3 );
			}
			
			// update last tile
			//cvResize(f, tile_tmp, 0);
			cvSetImageROI(buffer4gl, cvRect( 0, (tilenr-1) * tile_height, tile_width, tile_height) );
			cvResize(f, buffer4gl, 0);
			cvResetImageROI(buffer4gl);		

			GLenum format = IsBGR(buffer4gl->channelSeq) ? GL_BGR_EXT : GL_RGBA;
		
			glBindTexture(GL_TEXTURE_2D, texture[0]);
			glTexSubImage2D(GL_TEXTURE_2D, 0, 
				0, 0, 
				buffer4gl->width, buffer4gl->height, 
				format, GL_UNSIGNED_BYTE, 
				buffer4gl->imageData); 
		
			//cvReleaseImage( &tile_tmp );			

		} else {		
		
			GLenum format = IsBGR(f->channelSeq) ? GL_BGR_EXT : GL_RGBA;
		
			glBindTexture(GL_TEXTURE_2D, texture[0]);
			glTexSubImage2D(GL_TEXTURE_2D, 0, 
				0,  (tilenr -1) * tile_height, 
				frame->width, frame->height, 
				format, 
				GL_UNSIGNED_BYTE, 
				frame->imageData); 
		}	
		
	}
	
	if (flag_verbose) g_print("thread %s: gl upload took %.2fms\n",
		p_name,
		( (double)cvGetTickCount() - t ) / 
		( (double)cvGetTickFrequency()*1000.) 
	);			
}

void gl_zoom(IplImage *f) {
	if(f) {
			GLenum format = IsBGR(f->channelSeq) ? GL_BGR_EXT : GL_RGBA;

			frame_crop = cvCreateImage( cvSize( buffer4gl->width, f->height), 8, 3 );
			if (!texture[1]) {
				glGenTextures(1, &texture[1]);
				glBindTexture(GL_TEXTURE_2D, texture[1]);
				glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
				glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
				glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);

				cvSetImageROI(frame, cvRect( (f->width - buffer4gl->width)/2, 0, buffer4gl->width, f->height) );
				cvResize(f,frame_crop,0);
				cvResetImageROI(frame);					
							
				glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
					frame_crop->width, frame_crop->height,
					0, format, GL_UNSIGNED_BYTE, frame_crop->imageData);

			} else {
				glBindTexture(GL_TEXTURE_2D, texture[1]);				
				cvSetImageROI(f, cvRect( (f->width - buffer4gl->width)/2, 0, buffer4gl->width, f->height) );
				cvResize(f, frame_crop,0);
				cvResetImageROI(f);					
							
				glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
					frame_crop->width, frame_crop->height,
					0, format, GL_UNSIGNED_BYTE, frame_crop->imageData);

		
			}
			cvReleaseImage( &frame_crop );
		}	
}	

void gl_shiftTiles()
{
	char p_name[16];	
	prctl(PR_GET_NAME,p_name);	
	if (flag_verbose) g_print("thread %s: enter shift tiles\n", 	p_name);
	
	double t = (double)cvGetTickCount();
	int i;

	pthread_mutex_lock(&frame_mutex);
	if(frame) {	
		//shift tiles
		if (flag_downscale) {
			
			if (!tile_tmp)
				tile_tmp = cvCreateImage( cvSize( tile_width, tile_height), 8, 3 );
		
			for(i = 0; i < tilenr -1 ; i++) {			
				cvSetImageROI(buffer4gl, cvRect(0, (i+1) * tile_height, tile_width, tile_height) );
				cvResize(buffer4gl, tile_tmp, 0);
				cvResetImageROI(buffer4gl);
		
				cvSetImageROI(buffer4gl, cvRect( 0, (i) * tile_height, tile_width, tile_height) );
				cvResize(tile_tmp, buffer4gl, 0);
				cvResetImageROI(buffer4gl);
			}	
			//cvReleaseImage( &tile_tmp );

		} else {

			GLenum format = IsBGR(buffer4gl->channelSeq) ? GL_BGR_EXT : GL_RGBA;		
			glBindTexture(GL_TEXTURE_2D, texture[0]);
		
			for(i = tilenr ; i > 0; i--) {
				cvReleaseImage(&tilebuffer[i]);
				tilebuffer[i] = cvCloneImage(tilebuffer[i-1]);
				glTexSubImage2D(GL_TEXTURE_2D, 0, 
					0,  (tilenr - i - 2) * tile_height, 
					tilebuffer[i]->width, tilebuffer[i]->height,  
					format, 
					GL_UNSIGNED_BYTE, 
					tilebuffer[i]->imageData);			
			}

			cvReleaseImage(&tilebuffer[0]);
			tilebuffer[0] = cvCloneImage(frame);
			glTexSubImage2D(GL_TEXTURE_2D, 0, 
				0,  (tilenr - 2) * tile_height, 
				tilebuffer[i]->width, tilebuffer[i]->height,  
				format, 
				GL_UNSIGNED_BYTE, 
				frame->imageData);
		}
	}
	pthread_mutex_unlock(&frame_mutex);
	
	if (flag_verbose) g_print("thread %s: gl tileshift took %.2fms\n",
		p_name,
		( (double)cvGetTickCount() - t ) / 
		( (double)cvGetTickFrequency()*1000.) 
	);		
}

void gl_reshape(int width, int height)
{
  glViewport(0, 0, width, height); 
  glMatrixMode(GL_PROJECTION); 
  glLoadIdentity();
  gluOrtho2D(-width,width,-height,height);
  glMatrixMode(GL_MODELVIEW);
  if (flag_verbose)
	printf("reshaped\n");
}


void gl_draw() 
{
	static char p_name[16];
	if (!p_name)
		prctl(PR_GET_NAME,p_name);
		
	if (flag_verbose)
		g_print("thread %s: enter draw\n", 	p_name);
	
	double t = (double)cvGetTickCount();
	IplImage* frame_copy;

	pthread_mutex_lock(&last_full_frame_mutex);
	if (last_full_frame) {		
		gl_upload(last_full_frame);
		if(draw_zoom) gl_zoom(last_full_frame);
		//if(draw_zoom) gl_zoom(cvCloneImage(last_full_frame));
		gl_shiftTiles();
		cvReleaseImage( &last_full_frame );			
	}
	pthread_mutex_unlock(&last_full_frame_mutex);
		
	if(!flag_prescanned) {
		pthread_mutex_lock(&frame_mutex);
		if (frame) {
			//frame_copy =  cvCloneImage(frame);	
			gl_upload(frame);
			//cvReleaseImage( &frame_copy );
		}
		pthread_mutex_unlock(&frame_mutex);
	}

	glClearColor(0.0, 0.0, 0.0, 1.0);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	

	glLoadIdentity();        
    glTranslatef(0.0, 0.0, 0.0);
    glRotatef(90, 0, 0, 1); 
    glRotatef(180, 1, 0, 0);
        
    
    //double offset = ((2 / (double) tilenr / buf_height) * (double) scanline);
    double offset = 0.0;
    
    // make a quad for the main texture    
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D, texture[0]);
    glBegin(GL_QUADS);
        glTexCoord2f(0, 0); glVertex3f(-512, -512  - offset, 0);
        glTexCoord2f(1, 0); glVertex3f( 512, -512 - offset, 0);
        glTexCoord2f(1, 1); glVertex3f( 512,  512 - offset, 0);
        glTexCoord2f(0, 1); glVertex3f(-512,  512  - offset, 0);
    glEnd();
    glDisable(GL_TEXTURE_2D);

	// draw zoom in current tile
	if(draw_zoom)
	{
		glEnable(GL_TEXTURE_2D);
		glBindTexture(GL_TEXTURE_2D, texture[1]);
		glBegin(GL_QUADS);
			glTexCoord2f(0, 0); glVertex3f(-512, 512 -buf_height , 0.);
			glTexCoord2f(1, 0); glVertex3f( 512, 512 -buf_height , 0.);
			glTexCoord2f(1, 1); glVertex3f( 512, 512, 0.);
			glTexCoord2f(0, 1); glVertex3f(-512, 512, 0.);
		glEnd();
		glDisable(GL_TEXTURE_2D);

		glColor4f(1.0f, 1.0f, 1.0f, 0.5f);
		glBegin(GL_LINES);		
			glVertex3f(-512, 512 -buf_height , 0.);
			glVertex3f( 512, 512 -buf_height , 0.);
		glEnd();
	}

	
	glDisable(GL_TEXTURE_2D);

	// draw surrounding lines
	glColor4f(1.0f, 1.0f, 1.0f, 0.5f);
    glBegin(GL_LINES);
		glVertex3f(-512,-512 , 0.);
		glVertex3f(-512, 512 , 0.);
		
		glVertex3f( 512, -512, 0.);
		glVertex3f( 512, 512, 0.);
    glEnd();


    glRotatef(90, 0, 0, 1);

	// draw a line	
	glColor4f(1.0f, 1.0f, 1.0f, 1.0f);		
	if (draw_line > 0) { 
		glBegin(GL_LINES);
			glVertex3f(-512, 0.0, 0.0);
			glVertex3f( 512, 0.0, 0.0);
		glEnd();
	}

	// draw zoom in current tile
	if(draw_grey)
	{
		glColor4f(.5f, .5f, .5f, 1.0f);
		glBegin(GL_QUADS);
			glTexCoord2f(0, 0); glVertex3f(0. , -512 , 0.);
			glTexCoord2f(1, 0); glVertex3f(0. +buf_height, -512 , 0.);
			glTexCoord2f(1, 1); glVertex3f(0. +buf_height, 512, 0.);
			glTexCoord2f(0, 1); glVertex3f(0. , 512, 0.);
		glEnd();
		glDisable(GL_TEXTURE_2D);
	}	

	// write text info
	gl_write(-508, -520, str_info);
    gl_write(-508,  532, str_gps);
    gl_write(-508,  510, utc);
    
    glutSwapBuffers();

	if (flag_verbose) g_print("thread %s: draw function took %.2fms\n",
		p_name,
		( (double)cvGetTickCount() - t ) / 
		( (double)cvGetTickFrequency()*1000.)
	);

}


void gl_timer(){	
	glutPostRedisplay();
	glutTimerFunc(50,gl_timer,0);
}

void on_key_up(unsigned char key, int x, int y) {
	if (key == 'l') {
		draw_line = !draw_line;
	}
	else if (key == '+') {
		line_height++;
	}
	else if (key == '-') {
		if (line_height > 1) line_height--;
	}
	else if (key == 'z') {
		draw_zoom = !draw_zoom;
	}	
	else if (key == 'g') {
		draw_grey = !draw_grey;
	}
	else if (key == 'c') {
		flag_calib = !flag_calib;
	}
	else if (key == 'q') {
		waiting_eos = 1;
	}
}
	

void *gl_view_thread_func(void *arg) {
	char* argv = "";
	int argc = 0;
		
	prctl(PR_SET_NAME,"LS-DISPLAY",0,0,0);
	//signal(11,mysignal_handler);
	
	if (flag_verbose)
		printf("create view thread\n");
	
	glutInit(&argc,&argv);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
	glutInitWindowPosition(0,0);
	glutInitWindowSize(516,545);
	
	if (glutCreateWindow("linescan") == GL_FALSE) exit(1);

	gl_init();

	glutReshapeFunc(gl_reshape);
	glutDisplayFunc(gl_draw);
	glutTimerFunc(33, gl_timer, 0);
	glutKeyboardUpFunc(on_key_up);
	glutMainLoop();

	return 0;
}

int get_filesize(char* str, char* file)
{
	long long filesize;
	
	if( stat(file, &st) == -1)
			filesize = 0;
	else
		filesize = (st.st_size);

	if (filesize > (1024 * 1024 * 1024)) { // GB
		sprintf(str,"%.1f%s" , (double) filesize / (1024 * 1024 * 1024), "GB");
	} else if (filesize > (1024 * 1024)) {
		sprintf(str,"%.1f%s" , (double) filesize / (1024 * 1024), "MB");				
	} else if (filesize > (1024)) {
		sprintf(str,"%.1f%s" , (double) filesize / (1024), "KB");
	} else {
			sprintf(str,"%.1f%s" , (double) filesize, "B");
	}

	return 0;
}

void clear_frame(IplImage *frame) 
{
	//int x,y,j;
	//for(y = 0; y < frame->height; y++)
	//		for(x = 0; x < frame->width; x++)
	//		for (j = 0; j < 3; j++)
	//			frame->imageData[y * frame->width * 3 + x * 3 + j] = 0;
	bzero(frame->imageData,frame->height * frame->widthStep);
}


void write_images(IplImage *frame)
{
	char p_name[16];
	double tt;
	
	tt = (double)cvGetTickCount();
				
	char output_filename[255];
	sprintf(output_filename, "%s/img-%06ld.jpg", 
		output_dir, 
		outframecount);				
	if (flag_verbose)
		printf("thread %s: save to: %s\n",
			p_name, output_filename);
			
	if(!cvSaveImage(output_filename, frame, 0)) 
		printf("Could not save: %s\n",output_filename);
				
	if (flag_verbose)
		printf("thread %s: save image took %.2fms\n",
			p_name,
			((double)cvGetTickCount() - tt ) / 
			((double)cvGetTickFrequency()*1000.) );
}

void write_movie_frame(IplImage *frame)
{
	char p_name[16];
	double tt;
	
	tt = (double)cvGetTickCount();

	cvWriteFrame(writer,frame);
					
	if (flag_verbose) g_print("thread %s: save video frame took %.2fms\n",
		p_name,
		( (double)cvGetTickCount() - tt ) / 
		( (double)cvGetTickFrequency()*1000.) 
	);

	get_filesize(size_str,output_file);
}

void write_movie_start(IplImage *frame)
{
	CvSize imgSize;
	imgSize.width = frame->width;
	imgSize.height = frame->height;
			
	if (flag_verbose)
		printf("Write output to file: %s\n", output_file);

	writer = cvCreateVideoWriter( 
		output_file,
		CV_FOURCC('M','J','P','G'), quality, imgSize, 1);
		//CV_FOURCC('I', '4', '2', '0'), 100, imgSize, 1);
}

void calibration_apply(IplImage *image)
{
	IplImage* tmpimg;
	tmpimg = cvCloneImage(image);

	// substract darframe	
	if (darkframe) {
		if (darkframe->height != image->height || darkframe->width != image->width) {
			printf("darkframe has wrong image size! Do not apply calibration images!\n");
			flag_calib = 0;
		}
		else
			cvSub(image, darkframe, image,NULL);
	}

	// divide by flatframe
	if (flatframe) {
		if (flatframe->height != image->height || flatframe->width != image->width) {
			printf("flatframe has wrong image size! Do not apply calibration images!\n");
			flag_calib = 0;
		}
		else		
			cvDiv(tmpimg, flatframe, image, 150);
	}

	/*
	for(i = 0; i < last_full_frame->height; i++) {
		for(x = 0; x < last_full_frame->width; x++) {
			//printf("%d",(flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 1] );
			//printf(" %d",(last_full_frame->imageData + i * last_full_frame->widthStep)[x * last_full_frame->nChannels + 1] );
						
			if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 0] != 0)
				((uchar *)(last_full_frame->imageData + i * last_full_frame->widthStep))[x * last_full_frame->nChannels + 0] *=
					255/ ((uchar *)(flatframe->imageData + i * flatframe->widthStep))[x * flatframe->nChannels + 0];					
							
			if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 1] != 0)
				((uchar *)(last_full_frame->imageData + i * last_full_frame->widthStep))[x * last_full_frame->nChannels + 1] *=
					255/ ((uchar*)(flatframe->imageData + i * flatframe->widthStep))[x * flatframe->nChannels + 1];

			if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 2] != 0)
				((uchar *)(last_full_frame->imageData + i * last_full_frame->widthStep))[x * last_full_frame->nChannels + 2] *=
					255/ ((uchar *)(flatframe->imageData + i * flatframe->widthStep))[x * flatframe->nChannels + 2];
		}	
	}
	*/
}

// not yet working
void calibration_loadimages()
{
	// load darkframe
	darkframe = cvLoadImage("calibration/darkframe.jpg", 3);	
	if (!darkframe) {
		printf("Could not load darkframe.jpg");
		exit(1);
	}			

	flatframe = cvLoadImage("calibration/flatframe.jpg", 3);

	// load flatframe
	if (!flatframe) {
		printf("Could not load flatframe.jpg");
		exit(1);
	} else {
		IplImage *flat_normalized = cvCreateImage ( cvSize(flatframe->width,flatframe->height), IPL_DEPTH_8U, 1) ;
		int i, x;

		// find maxima
		for(i = 0; i < flatframe->height; i++) {
			for(x = 0; x < flatframe->width; x++) {
				if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 0] > max_b)
					max_b = (flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 0];

				if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 1] > max_g)
					max_g = (flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 1];

				if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 2] > max_r)
					max_r = (flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 2];																		

				if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 0] > max)
					max = (flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 0];

				if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 1] > max)
					max = (flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 1];

				if ((flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 2] > max)
					max = (flatframe->imageData + i * flatframe->widthStep)[x * flatframe->nChannels + 2];																		
			}				
		}

		// normalize
		
		for(i = 0; i < flatframe->height; i++) {
			for(x = 0; x < flatframe->width; x++) {

				((uchar *)(flatframe->imageData + i * flatframe->widthStep))[x * flatframe->nChannels + 0] *= 255 /max_g;
				((uchar *)(flatframe->imageData + i * flatframe->widthStep))[x * flatframe->nChannels + 1] *= 255 /max_g;
				((uchar *)(flatframe->imageData + i * flatframe->widthStep))[x * flatframe->nChannels + 2] *= 255 /max_r;

			}	
		}

		//cvShowImage("wind",flatframe);
		//cvSub(flatframe,darkframe,flatframe,NULL);		
	}	
}



static void process_buffer (GstElement *sink) {		
		int i, j, x, y;
		int r = 0;
		static int height, width;
		static char p_name[16];
				
		if (!p_name) {
			prctl(PR_GET_NAME,p_name);
		}
			
		GstElement *appsink = sink;			
		GstBuffer *buffer = 
			gst_app_sink_pull_buffer(GST_APP_SINK(appsink));		

		if (!buffer)
			printf("NO BUFFER\n");
			
		GstCaps *buff_caps = 
			gst_buffer_get_caps(buffer);
			
		assert(gst_caps_get_size(buff_caps) == 1);		

		//printf("thread %s: get frame structure\n", p_name);
		GstStructure* structure = 
			gst_caps_get_structure(buff_caps, 0);
		
		if(!gst_structure_get_int(structure, "width", &width) ||
			!gst_structure_get_int(structure, "height", &height))
			g_print("GStreamer: coud not get size from appsink \n");
		else
			framecount++;
		
		gst_caps_unref(buff_caps);

		if (flag_gps) {
			gps_askfordata();
		}				

		// input is already line-scanned image
		if (flag_prescanned) {

			outframecount++;
			
			if (flag_display) {
				pthread_mutex_lock(&last_full_frame_mutex);
				pthread_mutex_lock(&frame_mutex);
			}
			
			buf_height = height;
			
			if (!last_full_frame || last_full_frame->width != width) {
				last_full_frame = cvCreateImage(cvSize(width, height), IPL_DEPTH_8U, 3);
			}
			
			if (!frame || frame->width != width) {							
				frame = cvCreateImage(cvSize(width, height), IPL_DEPTH_8U, 3);
				//memcpy(frame->imageData, GST_BUFFER_DATA(buffer),
				//	frame->height * frame->widthStep);
			}
			

			if(!GST_BUFFER_DATA(buffer))
				printf("error: NO BUFFER DATA\n");					
			else {
				memcpy(last_full_frame->imageData, GST_BUFFER_DATA(buffer),
					last_full_frame->height * last_full_frame->widthStep);
				//last_full_frame->imageData = GST_BUFFER_DATA(buffer);
			}
			
			if (flag_calib) {
				calibration_apply(last_full_frame);
			}

			if ( (!writer || last_full_frame->width != width) && flag_write_movie) {
				write_movie_start(last_full_frame);	
						
			}				

			if(flag_write_images) {
				write_images(last_full_frame);
			}

			if(flag_write_movie) {
				write_movie_frame(last_full_frame);
			}
			
			line_height = frame->height;
				
			if (flag_display) {
				pthread_mutex_unlock(&last_full_frame_mutex);
				pthread_mutex_unlock(&frame_mutex);
			}

			if (flag_gps) {
				gps_log();
			}
		}
		// do real linescan
		else {
			
			//printf("thread %s: lock frame\n", p_name);
			if (flag_display)
				pthread_mutex_lock(&frame_mutex);		

			if (!frame || frame->width != width) {			
				printf("Create buffer frame [size: %dx%d]\n", width, buf_height);			
				frame = cvCreateImage(cvSize(width, buf_height), IPL_DEPTH_8U, 3);
				clear_frame(frame);					
			}

			if (flag_calib) {
				calibration_apply(frame);
			}			
		
			if ( (!writer || frame->width != width) && flag_write_movie) {
				write_movie_start(frame);						
			}
				
			if(!GST_BUFFER_DATA(buffer))
				printf("NO BUFFER DATA\n");

			// just copy 1 line
			for(i = 0; i < line_height && frame->height > scanline; i++) {
				/*for(x = 0; x < frame->width; x++) {
					((uchar *)(frame->imageData + (scanline) * frame->widthStep))[x * frame->nChannels + 0] =				
					//frame->imageData[scanline * frame->width * 3 + x * 3 + j] = 
					GST_BUFFER_DATA(buffer)[(height/2 + i)* frame->widthStep + x * frame->nChannels + 0]; // B
				
					((uchar *)(frame->imageData + scanline * frame->widthStep))[x * frame->nChannels + 1] =				
					//frame->imageData[scanline * frame->width * 3 + x * 3 + j] = 
					GST_BUFFER_DATA(buffer)[(height/2 + i) * frame->widthStep + x * frame->nChannels + 1]; // G
				
					((uchar *)(frame->imageData + scanline * frame->widthStep))[x*frame->nChannels + 2] =				
					//frame->imageData[scanline * frame->width * 3 + x * 3 + j] = 
					GST_BUFFER_DATA(buffer)[(height/2 + i) * frame->widthStep + x * frame->nChannels + 2]; // R
				}*/
				memcpy( (frame->imageData + (scanline) * frame->widthStep),
					GST_BUFFER_DATA(buffer)+((height/2 + i) * frame->widthStep),frame->widthStep);				
				scanline++;
			}
			
			if (i < line_height) {
				r = line_height - i;
			} else {
				r = 0;
			}

			if (flag_display) {
				pthread_mutex_unlock(&frame_mutex);		
			}
			
			// if buffer is full		
			if(scanline >= frame->height) {
						
				outframecount++;	
				scanline = 0;
			
				if (flag_verbose)
					g_print("thread %s: buffer [%02d] finished in %.2fms\n",
						p_name,
						(int) outframecount,
						( (double)cvGetTickCount() - tf ) / 
						( (double)cvGetTickFrequency()*1000.) );
		
				if(flag_write_images) {
					write_images(frame);
				}
			
				if(flag_write_movie) {
					write_movie_frame(frame);
				}
			
				if (flag_display) {
					//clone full frame for preview
					pthread_mutex_lock(&last_full_frame_mutex);
					last_full_frame = cvCloneImage(frame);
					pthread_mutex_unlock(&last_full_frame_mutex);
				
					//empty working frame
					pthread_mutex_lock(&frame_mutex);	
					clear_frame(frame);						
					pthread_mutex_unlock(&frame_mutex);						
				}
				
				// wenn line_height keine teiler von buffer höhe ist jetzt fortsetzen			
				
				if (r > 0) {
					if (flag_display) {
						pthread_mutex_lock(&frame_mutex);
					}
					for(i = line_height - r; i < line_height && frame->height > scanline; i++) {
						/*for(x = 0; x < frame->width; x++) {
							((uchar *)(frame->imageData + (scanline) * frame->widthStep))[x * frame->nChannels + 0] =				
							GST_BUFFER_DATA(buffer)[(height/2 + i) * frame->widthStep + x * frame->nChannels + 0]; // B
			
							((uchar *)(frame->imageData + scanline * frame->widthStep))[x * frame->nChannels + 1] =				
							GST_BUFFER_DATA(buffer)[(height/2 + i) * frame->widthStep + x * frame->nChannels + 1]; // G
			
							((uchar *)(frame->imageData + scanline * frame->widthStep))[x*frame->nChannels + 2] =				
							GST_BUFFER_DATA(buffer)[(height/2 + i) * frame->widthStep + x * frame->nChannels + 2]; // R
						}*/
						memcpy( (frame->imageData + (scanline) * frame->widthStep),
							GST_BUFFER_DATA(buffer)+((height/2 + i) * frame->widthStep),frame->widthStep);
						scanline++;
					}
					if (flag_display) {
						pthread_mutex_unlock(&frame_mutex);
					}					
				}				

				if (flag_gps) {
					gps_log();
				}		
			} // end buffer is full

		}
		
		
		gst_buffer_unref(buffer);

				
			
		fps_time += ((double)cvGetTickCount() - t);			
		
		if (framecount % 10 == 0) {
			fps = (1000.0 / ((fps_time/10.0)/((double)cvGetTickFrequency()*1000.)));
			fps_time = 0;
			if (flag_prescanned)
				fps *= (double) height / 2.0;			
		}

		long time_total = ((long)cvGetTickCount() - t_total)/((long)cvGetTickFrequency()*1000.);
		int hh = (time_total / 1000) / 3600;
		int mm = ((time_total / 1000) - hh * 3600 )/ 60;
		int ss = ((time_total / 1000) - mm * 60) % 60;
		
		if (flag_gps)
		 sprintf(str_info,"LH=%d | TIME=%02d:%02d:%02d | OUT=%s #%06ld | IN=#%06ld | FPS:%04.2f (%02.2fms) ",
			line_height,
			hh, mm, ss,
			size_str,
			outframecount,				
			framecount,
			fps ,			
			((double)cvGetTickCount() - t)/((double)cvGetTickFrequency()*1000.)	);
		else
		  sprintf(str_info,"LH=%d | TIME=%02d:%02d:%02d | OUT=%s #%06ld | IN=#%06ld | FPS:%04.2f (%02.2fms) ",
			line_height,
			hh, mm, ss,
			size_str,
			outframecount,				
			framecount,
			fps ,			
			((double)cvGetTickCount() - t)/((double)cvGetTickFrequency()*1000.)	);			
			

		printf("\r-> %s",str_info);
			
		if (flag_gps) {

			
					
			if (gpsfix.mode >= MODE_2D) {
				unix_to_iso8601(gpsfix.time, utc, sizeof(utc));
				sprintf(str_gps,
					"GPS=%s,  LAT=%.4f LON=%.4f ALT=%.0fm SPD=%.1fkm/h DIST=%.3fkm",
					gps_status_str,
					gpsfix.latitude,
					gpsfix.longitude,
					gpsfix.altitude,
					gpsfix.speed * MPS_TO_KPH,
					distance / 1000 );
			} else {
				sprintf(str_gps,
					"GPSFIX=%s", gps_status_str);
			}	
			//printf("%s",str_gps);
		}

		printf(" ");
			
		t = (double)cvGetTickCount();		
}


static void on_new_buffer (GstElement *element, gpointer data)
{
	static char p_name[16];
	if (!p_name) {
		prctl(PR_SET_NAME,"LS-GST",0,0,0);
		prctl(PR_GET_NAME,p_name);
	}

	process_buffer(element);

	/*GMainLoop *loop = (GMainLoop *) data;
	if (waiting_eos > 0) {
		//gst_element_send_event (GST_ELEMENT(element), gst_event_new_eos ());
		//gst_element_set_state (pipeline, GST_STATE_PAUSED);
		gst_element_set_state(GST_ELEMENT(element),GST_STATE_NULL);
		g_main_loop_quit(loop);
	}*/
		
	if (flag_verbose) printf("thread %s: has new buffer\n",
		p_name);
}

int inotify_watch()
{
	int length, i = 0;
	int fd;
	int wd;
	char buffer[I_BUF_LEN];
	char filename[255];
	
	// Initialize inotify
	if (watch_dir == NULL)
		watch_dir = "./";
		
	fd = inotify_init();
	if ( fd < 0 ) {
		perror( "inotify_init failed" );
	}
	wd = inotify_add_watch( fd, watch_dir, IN_CLOSE_WRITE );	

	printf("watch directory %s\n",watch_dir);
	
	// main loop
	int done = 0;	
	while ( !done ) {  
		framecount++;
		length = 0;
		i = 0;
		length = read( fd, buffer, I_BUF_LEN );  

		if ( length < 0 ) {
			perror( "read" );
		}  

		// got new image
		while ( i < length ) {
			struct inotify_event
				*event = ( struct inotify_event * ) &buffer[ i ];
   
			if ( event->len ) {
				if ( event->mask & IN_CLOSE_WRITE ) {					
					
					sprintf(filename, "%s/%s", watch_dir, event->name);										
					
					pthread_mutex_lock(&last_full_frame_mutex);
					last_full_frame = cvLoadImage(filename, 1);
					buf_height = last_full_frame->height;

					if (!frame) {
						frame = cvCloneImage(last_full_frame);
						clear_frame(frame);
					}

					if (flag_calib)
						calibration_apply(last_full_frame);

					if ( (!writer) && flag_write_movie) {
						write_movie_start(last_full_frame);
					}
					
					outframecount++;
								
			
					if(flag_write_movie) {
						write_movie_frame(last_full_frame);
					}
					pthread_mutex_unlock(&last_full_frame_mutex);
					
					if (flag_gps) {
						gps_askfordata();
						gps_log();
					}

					fps_time += ((double)cvGetTickCount() - t);			
		
					if (framecount % 20 == 0) {
							fps = (1000.0 / ((fps_time/20)/((double)cvGetTickFrequency()*1000.)));
							fps_time = 0;
					}

					long time_total = ((long)cvGetTickCount() - t_total)/((long)cvGetTickFrequency()*1000.);
					int hh = (time_total / 1000) / 3600;
					int mm = ((time_total / 1000) - hh * 3600 )/ 60;
					int ss = ((time_total / 1000) - mm * 60) % 60;		
		
					sprintf(str_info,"%02d:%02d:%02d [OUT%s #%06ld [IN] %s / FPS:%04.2f (%02.2fms) ",
						hh, mm, ss,
						size_str,
						outframecount,				
						filename,
						fps ,			
						((double)cvGetTickCount() - t)/((double)cvGetTickFrequency()*1000.)	);

					g_print("\r-> %s",str_info);
			
					if (flag_gps) {				
						if (gpsfix.mode >= MODE_2D) {
							sprintf(str_gps, "[GPS] %s, LAT: %.4f LON: %.4f ALT: %.0fm SPD: %.1fkm/h DIST: %.3fkm",
								gps_status_str,				
								gpsfix.latitude,
								gpsfix.longitude,
								gpsfix.altitude,
								gpsfix.speed * MPS_TO_KPH,
							distance / 1000 );
						} else {
							sprintf(str_gps, "[GPS] NO FIX");
						}	
						//printf("%s",str_gps);
					}

					printf("   ");

					// delete file
					if(remove(filename)) printf("Remove Error");
					
					t = (double)cvGetTickCount();
					
				}			
			}
		
		i += I_EVENT_SIZE + event->len;	

		}
	}
	printf("end watch: %s\n",watch_dir);
	inotify_rm_watch( fd, wd ); 
	close( fd );	
}

// gstreamer bus callback
static gboolean 
on_bus_call (GstBus *bus, GstMessage *msg, gpointer data) {
	
  GMainLoop *loop = (GMainLoop *) data;

  switch (GST_MESSAGE_TYPE (msg)) {

    case GST_MESSAGE_EOS:
		g_print ("\nGStreamer: (bus) End of stream\n");
		g_main_loop_quit(loop);
		pthread_kill(view_thread,SIGINT);
		exit(EXIT_SUCCESS);
		break;

    case GST_MESSAGE_ERROR: {
		gchar  *debug;
		GError *error;

		gst_message_parse_error (msg, &error, &debug);
		g_free (debug);

		g_printerr ("GStreamer: (bus) Error: %s\n", error->message);
		g_error_free (error);

		if(gst_element_set_state(GST_ELEMENT(pipeline), 
			GST_STATE_READY) == GST_STATE_CHANGE_FAILURE) {
			printf("GStreamer: unable to set pipeline to paused\n");
			gst_object_unref(pipeline);
			exit(EXIT_FAILURE);
		}      

		//g_main_loop_quit (loop);
		//exit(0);
		break;
    }
    
    default:
		break;
  }

  return TRUE;
}

gint g_timeout_func() {
	printf("XX\n");

	return 1;
}

gint main (gint argc, gchar *argv[]) {
	prctl(PR_SET_NAME,"LS-MAIN",0,0,0);

	GstElement *pipeline, *source;
	GstBus *bus;
	GMainLoop *loop;
	GstCaps *caps;
	
	read_config();
	read_options(argc, argv);

	// does not work anyway
	setlocale(LC_ALL,"C");

	// ifnorr sigsegv DANGEROUS!!!
	//signal(SIGSEGV,SIG_IGN);
	//signal(11,mysignal_handler);

	if (gst_pipeline == NULL)
		gst_pipeline = gst_default;

		if (gst_jp4pipeline == NULL)
		gst_jp4pipeline = "videotestsrc ! ffmpegcolorspace";	

	if(output_file == NULL) {
		time_t now;
		struct tm *curtime;
		now = time(NULL);
		curtime = gmtime(&now);
		char buf[255];
		strftime(buf, sizeof(buf), "%Y%m%d-%H%M%S.avi", curtime);
		output_file = buf;
		strcpy(output_file, buf);
	}

	char tmpstr[255] = "xx";
	char tmpout[255] = "yyyy";
	char tmppl[255] = "yyyy";
	strcpy(tmpout, output_file);
	strcpy(tmpstr, gst_jp4pipeline);
	

	if (flag_jp4) {
		flag_write_movie = 0;
		sprintf(tmppl, "%s", strtok(tmpstr,"OUTFILE"));		
		char * tmp;
		tmp = strtok(NULL,"OUTFILE");
		if (tmp != NULL) {
			strcat(tmppl, strtok(tmpout,"."));
			strcat(tmppl, tmp);
			//printf("%s%s%s\n\n", strtok(tmpstr,"OUTFILE"),output_file, strtok(NULL,"OUTFILE"));
		}
		gst_pipeline = tmppl;
	}	

	// init gps
	if (flag_gps)
		gps_setup();
		
	if (!flag_watcher_mode) {
		/* init GStreamer */
		gst_init (&argc, &argv);
		loop = g_main_loop_new (NULL, FALSE);
	 
		/* set up pipeline */
		printf("GStreamer: set up input pipeline: (%s)\n",gst_pipeline);
		strcat(gst_pipeline,"! appsink name=sink");
		pipeline = gst_parse_launch(gst_pipeline,NULL);

		/* set up bus */
		bus = gst_pipeline_get_bus (GST_PIPELINE (pipeline));
		gst_bus_add_watch (bus, on_bus_call, loop);
		gst_object_unref (bus);

		/* set up appsink */
		sink = gst_bin_get_by_name(GST_BIN(pipeline),"sink");
	
		g_object_set (G_OBJECT (sink), 
			"emit-signals", TRUE, 
			"sync", FALSE, 
			"max-buffers", 100,
			"drop",TRUE,
			NULL);
		
		g_signal_connect (G_OBJECT(sink), 
			"new-buffer",
			G_CALLBACK (on_new_buffer),
			loop);
	
		caps= gst_caps_new_simple("video/x-raw-rgb",
					"red_mask",   G_TYPE_INT, 255,
 	                "green_mask", G_TYPE_INT, 65280,
 	                "blue_mask",  G_TYPE_INT, 16711680,
                     NULL);
		gst_app_sink_set_caps(GST_APP_SINK(sink), caps);
		gst_caps_unref(caps);	

		// start gstreamer pipeline
		if(gst_element_set_state(GST_ELEMENT(pipeline), 
			GST_STATE_READY) == GST_STATE_CHANGE_FAILURE) {
				printf("GStreamer: unable to set pipeline to paused\n");
				gst_object_unref(pipeline);
				exit(0);
		}
		printf("GStreamer: pipline paused.\n");

		if(gst_element_set_state(GST_ELEMENT(pipeline), 
			GST_STATE_PLAYING) ==  GST_STATE_CHANGE_FAILURE) {
				printf("GStreamer: unable to set pipeline to play\n");
				gst_object_unref(pipeline);
				exit(0);
		}
		printf("GStreamer: pipline playing.\n");
	}

	if (flag_calib) {
		calibration_loadimages();		
	}	
  
  int result;
	// init viewer thread
	if (flag_display) {		
		result = pthread_mutex_init(&frame_mutex, NULL);
		if (result != 0) {
			perror("Mutex initialisation failed");
			exit(EXIT_FAILURE);
		}

		result = pthread_mutex_init(&last_full_frame_mutex, NULL);
		if (result != 0) {
			perror("Mutex initialisation failed");
			exit(EXIT_FAILURE);
		}		

		result = pthread_create(&view_thread, NULL, gl_view_thread_func, NULL);
		if (result != 0) {
			perror("Thread creation failed");
			exit(EXIT_FAILURE);
		}		
	}		

	
	// start tickers
	t = (double)cvGetTickCount();
	t_total = (double)cvGetTickCount();


	/* run main loop */	
	if (!flag_watcher_mode) {
		//g_timeout_add(1000, g_timeout_func, NULL);
		printf("now running...\n");
		g_main_loop_run (loop);
	}
	else {
		printf("running in watcher mode\n");
		inotify_watch();
	}

	/* exit */
	gst_element_set_state (pipeline, GST_STATE_NULL);
	gst_object_unref (pipeline);
	
	return 0;	
}

