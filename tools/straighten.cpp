/*
 * straighten
 * ===============================
 *
 * de-shake river/line-scan panorama images
 * 
*/

#include <memory.h>
#include <getopt.h>
#include "common.h"

#include "cv.h"
#include "highgui.h"


// hardcoded max limit for width of input image
// otherwise will segfault
const int MAXX = 20000;

int XS, YS;

// image buffers
uchar *IM; // image 
uchar *IMV; //vertical gradient image
uchar *IM1; //result image

uchar *IMB; //result image
uchar *IMG; //result image
uchar *IMR; //result image
uchar *IM1B; //result image
uchar *IM1G; //result image
uchar *IM1R; //result image

IplImage* img;
IplImage* imgc;
IplImage* out;

const int NO=18;
int XO[NO]={-10,-8,-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8,10};//xdelta
int dta[MAXX][NO];// ofsets between the vertical lines
int ssq[MAXX][NO];// distance between the vertical lines

const int MO=11;
const int RY=3;
int YO1[MO]={-3,-2,-1,-1,+0,+0,+1,+1,+2,+2,+3};//ydelta1
int YO2[MO]={+3,+2,+2,+1,+1,+0,+0,-1,-1,-2,-3};//ydelta2

double P[MAXX];//red curve
double Q[MAXX];//temporary curve
double R[MAXX];//intermediate curve
double W[MAXX];//weights

// files
char *output_file;
char *input_file;

int verbose = 0;
int color = 0;


__inline int valfr1(byte* pi, int pt, int ox, int oy, int shift)
{
	const int N=1<<shift;//=1
	long ix=ox>>shift, qx=ox&(N-1), rx=N-qx;
	long iy=oy>>shift, qy=oy&(N-1), ry=N-qy;

	byte* p=pi+(ix+iy*pt);
	long sum=long(*p++)*rx*ry;
	sum+=long(*p)*qx*ry; p+=pt;
	sum+=long(*p--)*qx*qy;
	sum+=long(*p)*rx*qy;

	return sum>>(shift+shift);
}

////

template <typename T>
class maximum
{
public:
	T m;
	int i;

public:
	maximum() : m(0), i(INVALID) {}

	void reset() { m=0; i=INVALID; }
	int add(int j, T u) { if (i==INVALID || u>m) { i=j; m=u; return 1; } else return 0; }
	int add(T u) { return add(0, u); }
	void add(T* p, int n) { for (int k=0; k<n; k++) add(k, p[k]); }

	T maxv() const { return m; }
	int maxi() const { return i; }

	bool isvalid() const { return i!=INVALID; }  
};

typedef maximum<double> maxd;
typedef maximum<int> maxn;

////

template <typename T>
class minimum
{
public:
	T m;
	int i;

public:
	minimum() : m(0), i(INVALID) {}

	void reset() { m=0; i=INVALID; }
	int add(int j, T u) { if (i==INVALID || u<m) { i=j; m=u; return 1; } else return 0; }
	int add(T u) { return add(0, u); }
	void add(T* p, int n) { for (int k=0; k<n; k++) add(k, p[k]); }

	T minv() const { return m; }
	int mini() const { return i; }

	bool isvalid() const { return i!=INVALID; }  
};

typedef minimum<double> mind;
typedef minimum<int> minn;


// print usage
void usage() {
	printf("Usage: straighten -i [INFILE] -o [OUTFILE]\n");
	printf("Options:\n");
	printf(" -o | --output FILE  input FILE \n");
	printf(" -i | --input FILE   output FILE\n");
	printf(" -h | --help         print this help\n");
	exit(0);
}


// read command line options	
void read_options(int argc, char *argv[]) {
	int c;
	
	static struct option long_options[] = {
		{"output", required_argument, 0, 'o'},
		{"input", required_argument, 0, 'i'},
		{"verbose",	no_argument, &verbose, 0},	
		{0, 0, 0, 0}
	};

	while(1) {
		int option_index = 0;
    
		c = getopt_long (argc, argv,"i:o:hv",long_options, &option_index);
		
		if (c == -1)
             break;
        
        switch(c) {
			
			case 0:
				break;
			
			case 'o':
				output_file = optarg;
				break;
			
			case 'i':
				input_file = optarg;
				break;
				
			case 'v':
				verbose = 1;				
				break;					
				
			case 'h':				
			default:
				usage();			
		}
	}
	
	if (!output_file) 
		output_file = "out.jpg";

	if (!input_file) {
		printf("need at leat an input file\n");
		usage();
	}
}


int main(int argc, char* argv[])
{
	read_options(argc, argv);

	//loading image
	imgc = cvLoadImage(input_file,-1);
	
	if (imgc->nChannels > 1) {
		color = 1;		
		img = cvLoadImage(input_file,CV_LOAD_IMAGE_GRAYSCALE);
	} else {
		img = imgc;
	}

	if(!img) {
		printf("Could not load image file: %s\n",input_file);
		return 1;
	} else {
		if (verbose) printf("Loaded file: %s\n",input_file);
		if (verbose) printf("dimensions %dx%dpx, channels: %d\n",img->width,img->height,imgc->nChannels);
	}
	XS=img->width;
	YS=img->height;

	// generate image buffer according to image size
	IM = (uchar *) malloc (XS*YS * sizeof(uchar));
	IMV = (uchar *) malloc (XS*YS * sizeof(uchar));
	IM1 = (uchar *) malloc (XS*YS * sizeof(uchar));

	if (color) {
		IMB = (uchar *) malloc (XS*YS * sizeof(uchar));
		IMG = (uchar *) malloc (XS*YS * sizeof(uchar));
		IMR = (uchar *) malloc (XS*YS * sizeof(uchar));		
		IM1B = (uchar *) malloc (XS*YS * sizeof(uchar));
		IM1G = (uchar *) malloc (XS*YS * sizeof(uchar));
		IM1R = (uchar *) malloc (XS*YS * sizeof(uchar));
	}
	
	int x,y;

	//convert opencv image to array (in a really stupid way)	
	for(x=0;x<XS;x++) {
		for(y=0;y<YS;y++) {
			IM[x+y*XS] = ((uchar *)(img->imageData + y*img->widthStep))[x];
			if (color) {
				IMB[x+y*XS] = ((uchar *)(imgc->imageData + y*imgc->widthStep))[x*imgc->nChannels];
				IMG[x+y*XS] = ((uchar *)(imgc->imageData + y*imgc->widthStep))[x*imgc->nChannels+1];
				IMR[x+y*XS] = ((uchar *)(imgc->imageData + y*imgc->widthStep))[x*imgc->nChannels+2];
			}
		}
	}
	

	//---------- important algo begins here

	//vertical gradient
	if (verbose) printf("calculate vertical gradient..\n");
	for (x=0; x<XS; x++)
	{
		for (y=0; y<YS; y++)
		{
			if (y<2||y+1>=YS) IMV[x+y*XS]=128;
			else IMV[x+y*XS]=int(IM[x+(y-2)*XS])+int(IM[x+(y-1)*XS])-int(IM[x+(y-1)*XS])-int(IM[x+(y-1)*XS])+128;
		}
	}

	//calculating ydeltas
	if (verbose) printf("calculate x&ydeltas...\n");	
	maxn ms;
	int no, x2, mo, y1, y2;
	for (x=0; x<XS; x++)
	{
		for (no=0; no<NO; no++) if (in(x2=x+XO[no],XS))
		{
			minn md;//minimalizator
			for (mo=0; mo<MO; mo++)
			{
				int sumsq=0;
				for (y=RY; y+RY<YS; y++)
				{
					y1=y+YO1[mo];
					y2=y+YO2[mo];

					int deltasq=square(int(IMV[x+y1*XS])-int(IMV[x2+y2*XS]));
//					if (deltasq>=square(8))
						sumsq+=deltasq;
				}
				md.add(YO2[mo]-YO1[mo],sumsq);
//				GD.point(0, x, sumsq/XS/10, COLOR12[mo],1);
			}
//			GD.point(0, x, md.minv()/XS/10, COLOR12[md.mini()],1);
			dta[x][no]=md.mini();//best fit between verticals
			ssq[x][no]=md.minv();//distance
			ms.add(md.minv());
		}
	}

	memset(P, 0, sizeof P);

	const double F1=1.;//force to zero
	const double F2=4000.;//ofset force
//	const double F3=400.;//smoothing force

	int t;
	//applying ofsets
	if (verbose) printf("apply offsets...\n");		
	for (t=0; t<400; t++)
	{
		memset(Q, 0, sizeof Q);
		memset(W, 0, sizeof W);

		for (x=0; x<XS; x++)
		{
			W[x]+=F1;

			for (no=0; no<NO; no++) if (in(x2=x+XO[no],XS))
			{
				int d=dta[x][no];
				int s=ssq[x][no];

//				if (s>100000) continue;

				double f=F2*.5/NO*corrfn(s,0,100000);
				W[x]+=f;
				Q[x]+=f*(P[x2]-d);

				W[x2]+=f;
				Q[x2]+=f*(P[x]+d);
			}

#if 0//smoothing > later
			if (x>0)
			{
				W[x]+=F3;
				Q[x]+=F3*P[x-1];
			}
			if (x+1<XS)
			{
				W[x]+=F3;
				Q[x]+=F3*P[x+1];
			}
#endif
		}
		for (x=0; x<XS; x++)
		{
			P[x]=Q[x]/W[x];
		}
	}

	//smoothing
	if (verbose) printf("smoothing\n");
	const double F4=1.;//force to intermediate curve
	const double F5=1.;//smoothing force
	memcpy(R, P, sizeof R);
	for (t=0; t<100; t++)
	{
		memset(Q, 0, sizeof Q);
		memset(W, 0, sizeof W);

		for (x=0; x<XS; x++)
		{
			Q[x]+=F4*R[x];
			W[x]+=F4;

			if (x>0)
			{
				W[x]+=F5;
				Q[x]+=F5*P[x-1];
			}
			if (x+1<XS)
			{
				W[x]+=F5;
				Q[x]+=F5*P[x+1];
			}
		}

		for (x=0; x<XS; x++)
		{
			P[x]=Q[x]/W[x];
		}
	}

	
	/*
	//drawing out the red line
	for (x=0; x<XS; x++)
	{
		GD.point(0, fix(x), fix(135.+P[x]), 0xFF, 1);
	}
	*/
	
	//result image
	if (verbose)  printf("calculate result images...\n");

	for (x=0; x<XS; x++)
	{
		for (y=0; y<YS; y++)
		{
			int y1=y+int(P[x]+.5);

			if (in(y1,YS))
			{
				//IM1[x+y*XS]=IM[x+y1*XS];
				
				if (color) {
					IM1B[x+y*XS]=valfr1(IMB, XS, 16*x, int(16.*(y+P[x])), 4);
					IM1G[x+y*XS]=valfr1(IMG, XS, 16*x, int(16.*(y+P[x])), 4);
					IM1R[x+y*XS]=valfr1(IMR, XS, 16*x, int(16.*(y+P[x])), 4);
				} else {
					IM1[x+y*XS]=valfr1(IM, XS, 16*x, int(16.*(y+P[x])), 4);
				}
				//((uchar *)(out->imageData + y*img->widthStep))[x] = IM[x+y1*XS];
			}
		}
	}

	//---------- important algo ends here	


	// now convert back to opencv image (very stupid!)

	if (color)
		out = cvCreateImage(cvSize(XS,YS),IPL_DEPTH_8U,3);
	else
		out = cvCreateImage(cvSize(XS,YS),IPL_DEPTH_8U,1);		
	
	for(x=0;x<XS;x++) {
		for(y=0;y<YS;y++) {
			
			if (color) {
				((uchar *)(out->imageData + y*imgc->widthStep))[x*imgc->nChannels] = IM1B[x+y*XS];
				((uchar *)(out->imageData + y*imgc->widthStep))[x*imgc->nChannels+1] = IM1G[x+y*XS];
				((uchar *)(out->imageData + y*imgc->widthStep))[x*imgc->nChannels+2] = IM1R[x+y*XS];
			} else {
				((uchar *)(out->imageData + y*imgc->widthStep))[x] = IM1[x+y*XS];
			}			
		}
	}	

	//save file
	if (verbose) printf("saving file %s\n",output_file);
	if(!cvSaveImage(output_file, out)) {
		printf("Could not save: file\n");
		return 1;
	}

	return 0;

}
