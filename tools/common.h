//common.h

#ifndef M_COMMON
#define M_COMMON

#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#ifdef using_vc
#pragma warning(disable:4996)
#endif

////

#define _THEPOS_ printf("@ %s %d\n", __FILE__, __LINE__);

#ifdef using_vc
#define _CRASH_ { _THEPOS_ __asm { int 3 }; }
#else
#define _CRASH_ { _THEPOS_ fflush(stdout); throw 0; }
#endif

////

#define tracen(c) {printf(#c##"=%d\n", (c));}
#define traced(c) {printf(#c##"=%f\n", (c));}

////

#undef assert

//#define use_assert
#ifdef use_assert

#define assert(c) { if (!(c)) _CRASH_ }

#define assmsg(c, s) { if (!(c)) { printf("! %s\n", s); _CRASH_ } }

#define assmsg1(c, s, a) { if (!(c)) { printf("! %s %d\n", s, (a)); _CRASH_ } }

#define assmsg2(c, s, a1, a2) { if (!(c)) { printf("! %s %d %d\n", s, (a1), (a2)); _CRASH_ } }

#define assmsg3(c, s, a1, a2, a3) { if (!(c)) { printf("! %s %d %d %d\n", s, (a1), (a2), (a3)); _CRASH_ } }

#define assmsg4(c, s, a1, a2, a3, a4) { if (!(c)) { printf("! %s %d %d %d %d\n", s, (a1), (a2), (a3), (a4)); _CRASH_ } }

#define asseqn(a,b) { int asseqna=(a), asseqnb=(b); if (asseqna!=asseqnb) { printf("!(%d == %d)\n", asseqna, asseqnb); _CRASH_ } }

#define asslessn(a,b) { int asseqna=(a), asseqnb=(b); if (asseqna>=asseqnb) { printf("!(%d < %d)\n", asseqna, asseqnb); _CRASH_ } }

#define assleqn(a,b) { int asseqna=(a), asseqnb=(b); if (asseqna>asseqnb) { printf("!(%d <= %d)\n", asseqna, asseqnb); _CRASH_ } }

#define asseqf(a,b,d) { double asseqfa=(a), asseqfb=(b); if (fabs(asseqfa-asseqfb)>(d)) { printf("!(%f == %f)\n", asseqfa, asseqfb); _CRASH_ } }

#define assdif(a,b,d) { double asseqfa=(a), asseqfb=(b); if (fabs(asseqfa-asseqfb)<(d)) { printf("!(%f != %f)\n", asseqfa, asseqfb); _CRASH_ } }

#else
#define assert(c)
#define assmsg(c, s)
#define assmsg1(c, s, a)
#define assmsg2(c, s, a1, a2)
#define assmsg3(c, s, a1, a2, a3)
#define assmsg4(c, s, a1, a2, a3, a4)
#define asseqn(a,b)
#define asslessn(a,b)
#define assleqn(a,b)
#define asseqf(a,b,d)
#define assdif(a,b,d)

#endif

////

//the character after the next 0
__inline void rownext(char*& p)
{
	assert(*p)
	while (*p++);
}

//tokenizal egy sort: AA\0BB\0CC\0\0
__inline int readrow(FILE* pf, char* row, int nrow, char* sep=0)
{
	int n=0, mode=0;
	for (int k=0; k<nrow; )
	{
		int c=fgetc(pf);
		if (feof(pf)) break;

		int issep=0;
		if (sep) { for (char* p=sep; *p; p++) if (c==*p) { issep=1; break; } }

		if (c==13) {}
		else if (c==10)
		{
			if (k+2>nrow) return -1;
			row[k++]=0;
			row[k++]=0;
			return n;
		}
		else if ((!sep) && (c==9 || c==32) || issep)
		{
			if (mode)
			{
				if (k+1>nrow) return -1;
				row[k++]=0;
				mode=0;
			}
		}
		else if (c>=0 && c<32)
		{
			return -1;
		}
		else
		{
			if (k+1>nrow) return -1;
			if (mode==0) n++;
			row[k++]=c;
			mode=1;
		}
	}

	return -1;
}

////

__inline int hexval(char c)
{
	return c>='0'&&c<='9'?int(c-'0'):
		c>='a'&&c<='f'?int(c-'a'+10):
		c>='A'&&c<='F'?int(c-'A'+10):-1;
}

////

typedef unsigned char byte;
typedef unsigned int num;

struct keyval
{
	int key;
	int val;
};

struct arrow
{
	int a, b;
	int val;
};

////

__inline int zerofn(int) { return 0; }
__inline int idfn(int k) { return k; }

////

//how many bit is needed to represent 'a'? (log2maj)
__inline unsigned nbit(unsigned a)
{
	int m;

#ifdef using_vc
	__asm bsr eax, a
	__asm jnz nbit_end
	__asm mov eax, 0xFFFFFFFF
nbit_end:
	__asm inc eax
	__asm mov m, eax

#else
	for (m=31; m>=0; m--) if ((1<<m)&a) break;
	m++;
#endif

	return m;
}

////

//the least significant bit
__inline unsigned sbit(unsigned a)
{
	int m;

#ifdef using_vc
	__asm bsf eax, a
	__asm jnz sbit_end
	__asm mov eax, 0xFFFFFFFF
sbit_end:
	__asm mov m, eax
#else
	if (a)
	{
		for (m=0; m<32; m++) if ((1<<m)&a) break;
	}
	else m=-1;
#endif

	return m;
}

//moves along the integers with 1-bit change (stop it at 2-power!)
//returns the actually changed bit
__inline unsigned crnext(unsigned& pos, unsigned& val)
{
	unsigned s=sbit(++pos);
	val^=1<<s;
	return s;
}

//usage:
//for (unsigned pos=0, val=0; pos<1<<G; crnext(pos, val)) { -thejob- }

////

//number of 1-bits
__inline int bwght(unsigned a)
{
	int s;
	for (s=0; a; a>>=1) if (a&1) s++;
	return s;
}

//bdist(a,b)=bwght(a^b)

////

//how many k-box is needed for n element
//e.g. up(n, 32) > how many int is needed for n bits
__inline int up(int n, int k)
{
	assert(n>0 && k>0)
	return (n-1)/k+1;
}

////

//bits [p .. p+w-1] in a
__inline int bits(int a, int p, int w) { return (a>>p) & ((1<<w)-1); }

__inline int byte0(int a) { return a&0xFF; }
__inline int byte1(int a) { return a>>8&0xFF; }
__inline int byte2(int a) { return a>>16&0xFF; }
__inline int byte3(int a) { return a>>24&0xFF; }

__inline int word0(int a) { return a&0xFFFF; }
__inline int word1(int a) { return a>>16&0xFFFF; }

__inline void splitword(int a, int& w0, int& w1) { w0=a&0xFFFF; w1=a>>16; }
__inline void splitbyte(int a, int& w0, int& w1) { w0=a&0xFF; w1=a>>8&0xFF; }

__inline void splitmod(int a, int n, int& w0, int& w1) { w0=a%n; w1=a/n; if (w0<0) { w0+=n; w1--; } }

__inline int nfr(double a, double& ar) { int ai=(int)floor(a); ar=a-ai; return ai; }


//splitrgb >

////

//cserel 2 elemet
template <typename T>
__inline void swapv(T& u, T& v) {  T w=u; u=v; v=w; }

//eloreforgat 3 elemet
template <typename T>
__inline void rotfv(T& u, T& v, T& w) {  T z=u; u=w; w=v; v=z; }

//visszaforgat 3 elemet
template <typename T>
__inline void rotbv(T& u, T& v, T& w) {  T z=u; u=v; v=w; w=z; }

//2 elemet rendez
template <typename T>
__inline void ordv(T& u, T& v) {  if (u>v) { T w=u; u=v; v=w; } }

//3 elemet rendez
template <typename T>
__inline void ordv(T& u, T& v, T& w)
{
	if (u>v) { T z=u; u=v; v=z; }
	if (v>w) { T z=w; w=v; v=z; }
	if (u>v) { T z=u; u=v; v=z; }
}

////

template <typename T>
__inline T absv(T u) { return u>=T(0)?u:-u; }

template <typename T>
__inline T deltav(T u, T v) { return u>=v?u-v:v-u; }

template <typename T>
__inline T signv(T u) { return u<0?-1:u>0; }

template <typename T>
__inline T signv(T u, T v) { return u<v?-1:u>v; }

template <typename T>
__inline int lexsgn1(T u1) { return u1<T(0)?-1:u1>T(0)?+1: 0; }

template <typename T>
__inline int lexsgn2(T u1, T u2) { return u1<T(0)?-1:u1>T(0)?+1: u2<T(0)?-1:u2>T(0)?+1: 0; }

template <typename T>
__inline int lexsgn3(T u1, T u2, T u3) { return u1<T(0)?-1:u1>T(0)?+1: u2<T(0)?-1:u2>T(0)?+1: u3<T(0)?-1:u3>T(0)?+1: 0; }

template <typename T>
__inline T minv(T u, T v) { return u<v?u:v; }

template <typename T>
__inline T minv(T u, T v, T w) { return minv<T>(minv<T>(u, v), w); }

template <typename T>
__inline T minv(T u, T v, T w, T z) { return minv<T>(minv<T>(u, v), minv<T>(w, z)); }

template <typename T>
__inline T maxv(T u, T v) { return u>v?u:v; }

template <typename T>
__inline T maxv(T u, T v, T w) { return maxv<T>(maxv<T>(u, v), w); }

template <typename T>
__inline T maxv(T u, T v, T w, T z) { return maxv<T>(maxv<T>(u, v), maxv<T>(w, z)); }

////
//u is limited by [a, b]

//a<b!!
template <typename T>
__inline T limitv(T u, T a, T b)
{
	assert(a<b)
	return u<a?a:u>b?b:u;
//	return minv<T>(maxv<T>(u, a), b);
}

////

template <typename T>
__inline T square(T u) { return u*u; }

template <typename T>
__inline T cube(T u) { return u*u*u; }

template <typename T>
__inline T pow4(T u) { return u*u*u*u; }

////

//n=4> ((c0*x/3+c1)*x/2+c2)*x+c3
template <typename T>
__inline T taylor(T* c, int n, T x)
{
	T t=c[0];
	for (int k=1; k<n; k++) t=t*x/T(n-k)+c[k];
	return t;
}

//n=4> ((c0*x+c1)*x+c2)*x+c3
template <typename T>
__inline T poly(T* c, int n, T x)
{
	T t=c[0];
	for (int k=1; k<n; k++) t=t*x+c[k];
	return t;
}

////

template <typename T>
void blockcopy(T* p0, int i0, const T* p1, int i1, int n)
{
	T* q0=p0+i0*n;
	const T* q1=p1+i1*n;
	for (int k=0; k<n; k++) q0[k]=q1[k];
}

////

//szimmetrikus v haromszogmatrix indexelese
__inline int symindex(int i, int j)
{
	assert(j>=0 && j<=i)
	return i*(i+1)/2+j;
}

//dinamikus matrix indexelese
__inline int dymindex(int i, int j)
{
	assert(j>=0 && i>=0)

	int m=i>=j?i:j;
	return m*m+(j<=i?j:2*m-i);
}

__inline void dymcoo(int n, int& i, int& j)
{
	assert(n>=0)

	int m=int(sqrt(double(n))), d=n-m*m;
	if (d<=m) { i=m; j=d; }
	else { i=2*m-d; j=m; }

}

////
//greatest common divisor, !!csak pozitivakra

__inline int gcd(int a, int b)
{
	int c;
	if (b>a) { c=b; b=a; a=c; }
	while ((c=a%b)) { a=b; b=c; }
	return b;
}

////

class gcdx
{
public:
	num ra, rb;
	num k0, m0;
	num k1, m1;
	num nstep;
	num quot;

public:
	gcdx(num a, num b)
		: ra(a), rb(b), k0(1), m0(0), k1(0), m1(1), nstep(0), quot(0) {}

	num next()
	{
		if (!rb) return 0xFFFFFFFF;
		//ra is the gcd
		//k0*a-m0*b is ra
		//m1/k1 is a/b simplified

		quot=ra/rb;
		num rem=ra%rb, w;
		w=quot*k1+k0; k0=k1; k1=w;
		w=quot*m1+m0; m0=m1; m1=w;
		ra=rb; rb=rem;

		nstep++;
		return quot;
	}

	void iter() { while (next()!=0xFFFFFFFF) ; }

public:

	num inva() const
	{
		assert(!rb && ra==1)
		return nstep&1 ? k1-k0 : k0;
		//inva*a%b==1
	}

	num invb() const
	{
		assert(!rb && ra==1)
		return nstep&1 ? m0 : m1-m0;
		//invb*b%a==1
	}

};

////

class cfract
{
public:
	int k0, m0;
	int k1, m1;
	int nstep;
	int quot;
	double r;

public:
	cfract(double _r) : k0(1), m0(0), k1(0), m1(1), nstep(0), quot(0), r(_r)  {}

	int next()
	{
		int w;
		if (fabs(r)<1e-8) return -1;

		quot=int(r); r-=quot; r=1./r;
		w=quot*k1+k0; k0=k1; k1=w;
		w=quot*m1+m0; m0=m1; m1=w;

		nstep++;
		return quot;
	}

	void iter(int n)
	{
		for (int i=0; i<n; i++) if (next()==-1) break;
	}

};

//usage>
//cfract cf(3.1415926);
//cf.iter(2);

////

__inline int factorial(int n)
{
	int p;
	for (p=1; n>0; n--) p*=n;
	return p;
}

__inline int binom(int n, int k)
{
	int p, q;
	for (p=1, q=1; q<=k; n--, q++) { p*=n; p/=q; }
	return p;
}

////

__inline int in(int a, int n) { return a<n && a>=0; }

__inline int in(int a, int n0, int n1) { return a>=n0 && a<n1; }
//__inline int between(int a, int n0, int n1) { return a>=n0 && a<n1; }

__inline int mod(int a, int n)
{
	int u=a%n;
	return n>0?(u<0?u+n:u):(u>0?u+n:u);
}

__inline int modchange(int a, int n, int m)
{
	assert(a>=0 && n>0 && m>0 && n%m==0)

	int k=(a%m)*(n/m)+a/m;
	assert(k>=0 && k<n)

	return k;
}

__inline int lower(int a, int n)
{
	int u=a%n;
	return u<0?a+n-u:a-u;
}

//returns k if n^k==a, else -1
__inline int ispow(int a, int n)
{
	assert(a>0 && n>0)
	int s;
	for (s=0; !(a%n); a/=n, s++) ;
	return a==1?s:-1;
}

////

//!!a and b in [0,n)
__inline int dmod(int a, int b, int n)
{
	return a<=b?minv(b-a, a+n-b):minv(a-b, b+n-a);
}

__inline int succ(int a, int n) { return (++a<n)?a:0; }

__inline int pred(int a, int n) { return a>0?a-1:n-1; }

//a/n==r/n && r%n==(a+b)%n
__inline int addinmod(int a, int b, int n)
{
	return mod(a+b,n)+lower(a,n);
}

////

//a++ (n)
//returns carry
__inline int modnext(int& a, int n) { if (++a==n) { a=0; return 1; } else return 0; }

//a*=2 (n) 
__inline int modmul2(int& a, int n) { if ((a+=a)>=n) { a-=n; return 1; } else return 0; }

////

const int INVALID=0x80000000;
const double INVALDD=1e300;

const int TEN6=1000000;
const double TEN6D=1000000.;

const double LOG2=log(2.);

const double HALFPI=atan2(1., 0.);//pi/2
const double ONEPI=HALFPI*2.;
const double TWOPI=HALFPI*4.;

const double SQRT2=sqrt(2.);
const double SQRT3=sqrt(3.);

const double SQRT2PI=sqrt(TWOPI);

////

const double PH_SPEEDLIGHT=299792458;// m/s
const double PH_EPS0=8.854187817e-12;// F/m
const double PH_PLANCK=6.626069311e-34;// Js
const double PH_DIRAC=PH_PLANCK/TWOPI;
const double PH_CHARGE=1.6021765314e-19;// C
const double PH_EMASS=9.109382616e-31;// kg

////

__inline double corrfn(double x, double m, double d)
{
	return exp(-square((x-m)/d));
}

__inline double gaussfn(double x, double m, double d)
{
	return exp(-.5*square((x-m)/d))/d/SQRT2PI;
}

////

__inline double sigma(double x) { return x<-12. ? 0. : x>+12. ? 1. : 1./(1.+exp(-x)) ; }

__inline double dsigma(double x) { return x*(1.-x); }

////

#ifdef using_vc
__inline double log2(double u) { return log(u)/LOG2; }

//log2 in millionth units
__inline int log2t6(int k) { return int(log2(double(k))*TEN6D); }
#endif

////

__inline double radtogrd(double fi, double N=360.) { if (fi<0.) fi+=TWOPI; return fi/TWOPI*N; }

__inline double grdtorad(double fi, double N=360.) { return fi/N*TWOPI; }

__inline void destopolar(double x, double y, double& r, double& fi) { r=sqrt(x*x+y*y); fi=atan2(y, x); }

__inline void polartodes(double r, double fi, double& x, double& y) { x=r*cos(fi); y=r*sin(fi); }

////

//[+1,-1] > [0,inf]
__inline double corrtodist(double c) { return sqrt(1.-c*c)/(1.+c); }

////

//hash
__inline num crc32b(byte *p, int n)
{
	num crc=0xFFFFFFFF;
	while (n--)
	{
		num r=(num)((crc & 0xFF) ^ *p++);
		for (int j=0; j<8; j++) if (r&1) r=(r>>1)^0xEDB88320; else r>>=1;
		crc=(crc>>8)^r;
	}
	return crc^0xFFFFFFFF;
}

__inline num crc32n(int *p, int n) { return crc32b((byte*)p, n*4); }

////

//signed random
__inline int rndint()
{
#ifdef WIN32
	int a=rand(), b=rand(), c=rand();
	return a^(b<<8)^(c<<17);
#else
	return rand();
#endif
}

//unsigned random
__inline num rndnum()
{
#ifdef WIN32
	int a=rand(), b=rand(), c=rand();
	return a^(b<<8)^(c<<16);
#else
	return rand()^(rand()<<16);
#endif
}

//random modular
__inline int rndmod(int n)
{
#ifdef WIN32
	int a=rand(), b=rand();
	return (a+(b<<15))%n;
#else
	return rand()%n;
#endif
}

//excluding a
__inline int rndmodx(int n, int a)
{
	int b=rndmod(n-1);
	return b<a?b:b+1;
}

//random in interval [0,1]
__inline double rnd01()
{
	double w;
#ifdef WIN32
	int a=rand(), b=rand();
	w=double(a+(b<<15))/double(0x3FFFFFFF);
#else
	w=double(rand())/double(0x7FFFFFFF);
#endif

	assert(w>=0. && w<=1.)
	return w;
}

//[-1, +1]
__inline double rndunit() { return 2.*rnd01()-1.; }

__inline double rndnormal(double* w=0)
{
	double v1, v2, rsq, z;
	do
	{
		v1=2.*rnd01()-1.;//[-1,+1]
		v2=2.*rnd01()-1.;
		rsq=v1*v1+v2*v2;
	}
	while (rsq>=1. || rsq==0.);

	z=sqrt(-2.*log(rsq)/rsq);
	if (w) *w=v2*z;//v2*z also good
	return v1*z;
}

//P(0)=p, P(1)=pq, P(2)=pqq, etc
__inline int rndlevel(double p)
{
	assert(p>0. && p<1.)

	int l=0;
	while (l<1000 && rnd01()>=p) l++;
	return l;
}

////

//kullback leibner distance (2 normal distribution, relative entropy)
__inline double KLdta(double m1, double d1, double m2, double d2)
{
	return log(d2/d2)+.5*(square(d2)+square(m1-m2))/square(d2)-.5;
}

////

//ket minta (m=atlag, d=szorasnegyzet, w=suly) osszegenek szorasa
__inline double d2sum(double m1, double d1, double w1,  double m2, double d2, double w2)
{
//	double w=w1+w2;
	double p1=w1/(w1+w2), p2=1.-p1;
	double m12=m1-m2;

//	return (w1*d1+w2*d2+m12*m12*w1*w2/w)/w;
	return p1*d1+p2*d2+m12*m12*p1*p2;
}

//wr <- w1+w2
//mr <- (w1*m1+w2*m2)/(w1+w2)
//dr <- d2sum
__inline void d2sum(double m1, double d1, double w1,  double m2, double d2, double w2, double& m, double& d, double& w)
{
//	double w=w1+w2;
	double p1=w1/(w1+w2), p2=1.-p1;
	double m12=m1-m2;

//	d=(w1*d1+w2*d2+m12*m12*w1*w2/w)/w;
	w=w1+w2;
	m=p1*m1+p2*m2;
	d=p1*d1+p2*d2+m12*m12*p1*p2;
}

//d2=0, w2=1 (egy pont hozzaadasa)
__inline double d2sum(double m1, double d1, double w1,  double a2)
{
//	double w=w1+1;
	double p1=w1/(w1+1.), p2=1.-p1;
	double m12=m1-a2;

//	return (w1*d1+m*m*w1/w)/w;
	return p1*d1+m12*m12*p1*p2;
}

////

//crosses the bits of a and b
__inline num cross(num a, num b)
{
	num r=rndnum();
	return (a&r)|(b&~r);
}

////

__inline int stavg(int s1, int sx) { return s1?(sx+(s1>>1))/s1:0; }

__inline double stavg(double s1, double sx) { return s1>0.?sx/s1:0.; }

#ifdef using_vc
#pragma warning(disable:4035)
__inline int stdev(int s1, int sx, int sxx)//(sxx-sx*sx/s1)/s1
{
	__asm mov eax, sx
	__asm neg eax
	__asm imul sx
	__asm idiv s1
	__asm add eax, sxx
	__asm cdq
	__asm idiv s1
}
#pragma warning(default:4035)

#else
__inline int stdev(int s1, int sx, int sxx)//(sxx-sx*sx/s1)/s1
{
	if (s1==0) return 0;
	double s1d=double(s1);
	double d=(double(sxx)-double(sx)*double(sx)/s1d)/s1d;
	return int(d);
}
#endif

__inline double stdev(double s1, double sx, double sxx)//(sxx-sx*sx/s1)/s1
{
	return s1>0.?(sxx-sx*sx/s1)/s1:0.;
}

#ifdef using_vc
#pragma warning(disable:4035)
__inline int muldiv(int a, int b, int c)//a*b/c
{
	__asm mov eax, a
	__asm imul b
	__asm idiv c
}
#pragma warning(default:4035)
#endif

////

__inline int nsq(int nx, int ny) { return nx*nx+ny*ny; }
__inline int nmx(int nx, int ny) { int dx=absv(nx), dy=absv(ny); return dx>dy?dx:dy; }
__inline int nr4(int nx, int ny) { return absv(nx)+absv(ny); }
__inline int nr8(int nx, int ny) { int dx=absv(nx), dy=absv(ny); return dx>dy?dx+(dx<<2)+(dy<<1):dy+(dy<<2)+(dx<<1); }

__inline int pos(int px, int py, int qx, int qy, int rx, int ry) { return (qx-px)*(ry-py)-(rx-px)*(qy-py); }
__inline int dot(int px, int py, int qx, int qy, int rx, int ry) { return (px-qx)*(rx-qx)+(py-qy)*(ry-qy); }
__inline int dsq(int px, int py, int qx, int qy) { int dx=qx-px, dy=qy-py; return dx*dx+dy*dy; }

__inline int dmx(int px, int py, int qx, int qy) { int dx=absv(qx-px), dy=absv(qy-py); return dx>dy?dx:dy; }
__inline int dr4(int px, int py, int qx, int qy) { return absv(qx-px)+absv(qy-py); }
__inline int dr8(int px, int py, int qx, int qy) { int dx=absv(qx-px), dy=absv(qy-py); return dx>dy?dx+(dx<<2)+(dy<<1):dy+(dy<<2)+(dx<<1); }

__inline int dis(int px, int py, int qx, int qy, int N=1) { return (int)(sqrt(double(dsq(px, py, qx, qy))*N)+.5); }
__inline int ang(int px, int py, int qx, int qy, int N=360)
{
	double fi=atan2(double(qy-py), double(qx-px)); if (fi<0.) fi+=TWOPI;
	int nfi=int(floor(fi/TWOPI*N+.5)); if (nfi>=N) nfi-=N;
	return nfi;
}

////

__inline double posf(double px, double py, double qx, double qy, double rx, double ry) { return (qx-px)*(ry-py)-(rx-px)*(qy-py); }
__inline double dotf(double px, double py, double qx, double qy, double rx, double ry) { return (px-qx)*(rx-qx)+(py-qy)*(ry-qy); }
__inline double dsqf(double px, double py, double qx, double qy) { double dx=qx-px, dy=qy-py; return dx*dx+dy*dy; }

__inline double nrsq(double nx, double ny) { return nx*nx+ny*ny; }
__inline double norm(double nx, double ny) { return sqrt(nx*nx+ny*ny); }

__inline void normalize(double& nx, double& ny)
{
	double nr=sqrt(nx*nx+ny*ny);
	if (fabs(nr)>1e-8)
	{
		nx/=nr;
		ny/=nr;
	}
}

__inline void rotfi(double& nx, double& ny, double fi)
{
	double cfi=cos(fi), sfi=sin(fi);
	double nx1=cfi*nx-sfi*ny;
	double ny1=sfi*nx+cfi*ny;

	nx=nx1;
	ny=ny1;
}

//gorbulet pqr menten
//pozitiv ha oramutato jarasaval ellentetesen kanyarodik
__inline double curv(double px, double py, double qx, double qy, double rx, double ry)
{
	double dsq1=dsqf(px, py, qx, qy);
	double dsq2=dsqf(qx, qy, rx, ry);
	assert(dsq1>1e-8 && dsq2>1e-8)

	double area=posf(px, py, qx, qy, rx, ry);
	double dsq0=dsqf(px, py, rx, ry);

//	return 4.*square(area)/dsq0/dsq1/dsq2;//sq
	return 2.*area/sqrt(dsq0*dsq1*dsq2);
}

//gorbuleti vektor
__inline void curv(double px, double py, double qx, double qy, double rx, double ry, double& kx, double& ky)
{
	double d0=dsqf(px, py, qx, qy);
	double d1=dsqf(rx, ry, qx, qy);
	assert(d0>1e-8 && d1>1e-8)

	kx=(px-qx)/d0+(rx-qx)/d1;
	ky=(py-qy)/d0+(ry-qy)/d1;
}

__inline double modf(double val, double period)
{
	double val1=val-floor(val/period)*period;
	if (val1>=period) val1-=period;//sajnos kell
	assert(val1>=0. && val1<period)
	return val1;
}

__inline double fitbyperiod(double val, double preval, double period=TWOPI)
{
	double delta=val-preval;
	double val1=val-floor((delta+.5*period)/period)*period;

	assert(fabs(val1-preval)<=.5*period)
	return val1;
}

//3 pontra illesztett kor kozeppontja
__inline double centre(double px, double py, double qx, double qy, double rx, double ry, double& kx, double& ky)
{
	double dx1=px-qx, dy1=py-qy;
	double dx2=rx-qx, dy2=ry-qy;

	double q1=square(dx1)+square(dy1);
	double q2=square(dx2)+square(dy2);

	double det=2.*(dx1*dy2-dy1*dx2);
	kx=qx+(+q1*dy2-q2*dy1)/det;
	ky=qy+(-q1*dx2+q2*dx1)/det;

	return sqrt(square(kx-qx)+square(ky-qy));
}

//p=pa*a+pb*b
__inline void linsol2(double ax, double ay, double bx, double by, double px, double py, double& fa, double& fb)
{
	double det=ax*by-ay*bx;
	if (fabs(det)<1e-8) { fa=0.; fb=0.; return; }

	fa=(+by*px-bx*py)/det;
	fb=(-ay*px+ax*py)/det;

//	assert(fabs(ax*fa+bx*fb-px)<1e-8 && fabs(ay*fa+by*fb-py)<1e-8)
}

__inline void linsol2(double* m, double* v, double* r)
{
	double det=m[0]*m[3]-m[1]*m[2];
	if (fabs(det)<1e-8) { r[0]=0.; r[1]=0.; return; }

	r[0]=(+m[3]*v[0]-m[2]*v[1])/det;
	r[1]=(-m[1]*v[0]+m[0]*v[1])/det;
}

////

const int dir8x[8]={ 1,1,0,-1,-1,-1, 0, 1, };
const int dir8y[8]={ 0,1,1, 1, 0,-1,-1,-1, };

const int dir4x[4]={ 1,0,-1, 0, };
const int dir4y[4]={ 0,1, 0,-1, };

//alternative
//const int* dx4=dir4x;
//const int* dy4=dir4y;
/* const int dx4[4]={ 1,0,-1, 0, };
 const int dy4[4]={ 0,1, 0,-1, }; */ // moved to level.cpp

////

const int COLOR12[12]=
{
	0x0000FF, 0x0080FF, 0x00FFFF, 0x00FF80, 0x00FF00, 0x80FF00,
	0xFFFF00, 0xFF8000, 0xFF0000, 0xFF0080, 0xFF00FF, 0x8000FF,
};

__inline int color12(int c, int w)
{
	if (!in(c, 12)) return 0;

	int u=COLOR12[c];
	int r=limitv((u&0xFF)*w/255, 0, 255);
	int g=limitv((u>>8&0xFF)*w/255, 0, 255);
	int b=limitv((u>>16&0xFF)*w/255, 0, 255);

	return r|g<<8|b<<16;
}

//255*6=1530 values
__inline int hue2color(int h, int w=255)
{
	int hm=mod(h,255), hc=mod(h/255,6);

	int r=(hc==5||hc==0) ? 0xFF : hc==1 ? 0xFF-hm : hc==4 ? hm : 0;
	int g=(hc==1||hc==2) ? 0xFF : hc==3 ? 0xFF-hm : hc==0 ? hm : 0;
	int b=(hc==3||hc==4) ? 0xFF : hc==5 ? 0xFF-hm : hc==2 ? hm : 0;

	if (in(w,255)) { r=r*w/255; g=g*w/255; b=b*w/255; }

	return r|g<<8|b<<16;
}

//szincsatornak megforditasa
__inline int revcolor(int w) { return (w>>16&0x0000FF) | (w&0x00FF00) | (w<<16&0xFF0000); }

//szurkeertek
__inline int grayvalue(int w) { return ((w&0xFF)+(w>>8&0xFF)+(w>>16&0xFF)+1)/3; }

//rgb
__inline void splitrgb(int a, int& w0, int& w1, int& w2) { w0=a&0xFF; w1=a>>8&0xFF; w2=a>>16&0xFF; }

__inline int packrgb(int r, int g, int b) { return limitv(r, 0, 255)|limitv(g, 0, 255)<<8|limitv(b, 0, 255)<<16; }

__inline int packgray(int g) { int g1=limitv(g, 0, 255); return g1|g1<<8|g1<<16; }

////

//gradiensvektor
template <typename T>
__inline T GRADX(T* p, int pt)
{
	return (p[-pt+1]+p[+1]+p[+pt+1]-p[-pt-1]-p[-1]-p[+pt-1])/T(6);
}

template <typename T>
__inline T GRADY(T* p, int pt)
{
	return (p[+pt-1]+p[+pt]+p[+pt+1]-p[-pt-1]-p[-pt]-p[-pt+1])/T(6);
}

//szintvonal vektorgorbulet, returns cos-angle
__inline double CURVXY(double* p, int pt, double& kx, double& ky)
{
	double dx[8], dy[8], v1;
	int dn=0, o1, o2;

	//x=+1
	v1=+1.; o1=+1; o2=+1+pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dx[dn]=v1; dy[dn++]=+(*p-p[o1])/(p[o2]-p[o1]); }
	o2=+1-pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dx[dn]=v1; dy[dn++]=-(*p-p[o1])/(p[o2]-p[o1]); }

	//x=-1
	v1=-1.; o1=-1; o2=-1+pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dx[dn]=v1; dy[dn++]=+(*p-p[o1])/(p[o2]-p[o1]); }
	o2=-1-pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dx[dn]=v1; dy[dn++]=-(*p-p[o1])/(p[o2]-p[o1]); }

	//y=+1
	v1=+1.; o1=+pt; o2=+1+pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dy[dn]=v1; dx[dn++]=+(*p-p[o1])/(p[o2]-p[o1]); }
	o2=-1+pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dy[dn]=v1; dx[dn++]=-(*p-p[o1])/(p[o2]-p[o1]); }

	//y=-1
	v1=-1.; o1=-pt; o2=+1-pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dy[dn]=v1; dx[dn++]=+(*p-p[o1])/(p[o2]-p[o1]); }
	o2=-1-pt;
	if ((p[o1]<=*p && p[o2]>*p) || (p[o1]>=*p && p[o2]<*p)) { dy[dn]=v1; dx[dn++]=-(*p-p[o1])/(p[o2]-p[o1]); }

	if (dn!=2)
	{
		kx=0.; ky=0.; return 0.;
	}

	double d0=square(dx[0])+square(dy[0]);
	double d1=square(dx[1])+square(dy[1]);

	kx=dx[0]/d0+dx[1]/d1;
	ky=dy[0]/d0+dy[1]/d1;

	return (dx[0]*dx[1]+dy[0]*dy[1])/sqrt(d0*d1);
}

////

//kepintenzitas tortpozicioban
//(ox oy) shift-bit fixed pos
__inline int valfr(byte* pi, int pt, int ox, int oy, int shift)
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

//x must be an ordered set
__inline int linsample(double* x, double* y, const int n, double* u, const int nsmp, const double x0, const double x1)
{
	assert(x0<x1 && nsmp>0)

	const double gap=(x1-x0)/(nsmp-1);
	assert(x0>=x[0])

	double xw=x0;
	int k=0, j=0;
	while (j<nsmp && k<n)
	{
		assert(x[k]<=xw)

		if (k+1<n && x[k+1]<=xw)
		{
			k++;
		}
		else
		{
			if (x[k]==xw)
			{
				u[j++]=y[k];
			}
			else
			{
				if (k+1>=n) break;
//				assert(k+1<n)
//				assert(xw<x[k+1])
				double ratio=(xw-x[k])/(x[k+1]-x[k]);

				u[j++]=y[k]+ratio*(y[k+1]-y[k]);
			}
			xw+=gap;
		}
	}

	return j;
}

#if 0
	double x1[3]={0,2,2,3};
	double y1[3]={10,12,13,11};
	double x2[4]={0,2,2,3};
	double y2[4]={10,12,13,11};
	double u[16];
	linsample(x1, y1, 3, u, 6, 1., 2.5);
	linsample(x1, y1, 3, u, 6, 0., 3.);
	linsample(x2, y2, 4, u, 7, 0., 3.5);
#endif

////
//sound

__inline double cent2ratio(double v) { return pow(2., v/1200.); }

const double C1LOGF=1200./log(2.);
__inline double ratio2cent(double r) { return log(r)*C1LOGF; }

// const double CR100=cent2ratio(100);

//v in [-1.,+1.]
__inline int unitval2color(double v)
{
	const double F2=511.99;
	const double F4=1020.;//254.*4.;

	v=limitv(v, -1., +1.);

	if (v<0.)
	{
		v=-v;
		if (v<.25) return int(v*F4);
		else if (v<.5) return int((v-.25)*F4)<<8|0xFF;
		else return int((v-.5)*F2)<<16|0xFFFF;
	}
	else
	{
		if (v<.25) return int(v*F4)<<16;
		else if (v<.5) return int((v-.25)*F4)<<8|0xFF0000;
		else return int((v-.5)*F2)|0xFFFF00;
	}
}


////

#endif//M_COMMON
