#include "npb-C.h"
#include "global.h"
static void evolve(dcomplex u0[NZ][NY][NX], dcomplex u1[NZ][NY][NX],
		   int t, int indexmap[NZ][NY][NX], int d[3]);
static void compute_initial_conditions(dcomplex u0[NZ][NY][NX], int d[3]);
static void ipow46(double a, int exponent, double *result);
static void setup(void);
static void compute_indexmap(int indexmap[NZ][NY][NX], int d[3]);
static void print_timers(void);
static void fft(int dir, dcomplex x1[NZ][NY][NX], dcomplex x2[NZ][NY][NX]);
static void cffts1(int is, int d[3], dcomplex x[NZ][NY][NX],
		   dcomplex xout[NZ][NY][NX],
		   dcomplex y0[NX][FFTBLOCKPAD],
		   dcomplex y1[NX][FFTBLOCKPAD]);
static void cffts2(int is, int d[3], dcomplex x[NZ][NY][NX],
		   dcomplex xout[NZ][NY][NX],
		   dcomplex y0[NX][FFTBLOCKPAD],
		   dcomplex y1[NX][FFTBLOCKPAD]);
static void cffts3(int is, int d[3], dcomplex x[NZ][NY][NX],
		   dcomplex xout[NZ][NY][NX],
		   dcomplex y0[NX][FFTBLOCKPAD],
		   dcomplex y1[NX][FFTBLOCKPAD]);
static void fft_init (int n);
static void cfftz (int is, int m, int n, dcomplex x[NX][FFTBLOCKPAD],
		   dcomplex y[NX][FFTBLOCKPAD]);
static void fftz2 (int is, int l, int m, int n, int ny, int ny1,
		   dcomplex u[NX], dcomplex x[NX][FFTBLOCKPAD],
		   dcomplex y[NX][FFTBLOCKPAD]);
static int ilog2(int n);
static void checksum(int i, dcomplex u1[NZ][NY][NX], int d[3]);
static void verify (int d1, int d2, int d3, int nt,
		    boolean *verified, char *class);
int main(int argc, char **argv) {
    int i, ierr;
    static dcomplex u0[NZ][NY][NX];
    static dcomplex pad1[3];
    static dcomplex u1[NZ][NY][NX];
    static dcomplex pad2[3];
    static dcomplex u2[NZ][NY][NX];
    static dcomplex pad3[3];
    static int indexmap[NZ][NY][NX];
    int iter;
    int nthreads = 1;
    double total_time, mflops;
    boolean verified;
    char class;
    for (i = 0; i < T_MAX; i++) {
	timer_clear(i);
    }
    setup();
    compute_indexmap(indexmap, dims[2]);
    compute_initial_conditions(u1, dims[0]);
    fft_init (dims[0][0]);
    fft(1, u1, u0);
    for (i = 0; i < T_MAX; i++) {
	timer_clear(i);
    }
    timer_start(T_TOTAL);
    if (TIMERS_ENABLED == TRUE) timer_start(T_SETUP);
    compute_indexmap(indexmap, dims[2]);
    compute_initial_conditions(u1, dims[0]);    
    fft_init (dims[0][0]);
    if (TIMERS_ENABLED == TRUE) {
      timer_stop(T_SETUP);
    }
    if (TIMERS_ENABLED == TRUE) {
      timer_start(T_FFT);
    }
    fft(1, u1, u0);
    if (TIMERS_ENABLED == TRUE) {   
      timer_stop(T_FFT);
    }
    for (iter = 1; iter <= niter; iter++) {
	    if (TIMERS_ENABLED == TRUE) {     
	      timer_start(T_EVOLVE);
	    }
	    evolve(u0, u1, iter, indexmap, dims[0]);
            if (TIMERS_ENABLED == TRUE) {    
	      timer_stop(T_EVOLVE);
	    }
            if (TIMERS_ENABLED == TRUE) {  
	      timer_start(T_FFT);
	    }
            fft(-1, u1, u2);
            if (TIMERS_ENABLED == TRUE) {      
	      timer_stop(T_FFT);
	    }
            if (TIMERS_ENABLED == TRUE) {     
	      timer_start(T_CHECKSUM);
	    }	
            checksum(iter, u2, dims[0]);
            if (TIMERS_ENABLED == TRUE) {   
	      timer_stop(T_CHECKSUM);
	    }
    }
    verify(NX, NY, NZ, niter, &verified, &class);
    nthreads = omp_get_num_threads();
#endif     
  } 
    timer_stop(T_TOTAL);
    total_time = timer_read(T_TOTAL);
    if( total_time != 0.0) {
	mflops = 1.0e-6*(double)(NTOTAL) *
	    (14.8157+7.19641*log((double)(NTOTAL))
	     +  (5.23518+7.21113*log((double)(NTOTAL)))*niter)
	    /total_time;
    } else {
	mflops = 0.0;
    }
    c_print_results("FT", class, NX, NY, NZ, niter, nthreads,
		    total_time, mflops, "          floating point", verified, 
		    NPBVERSION, COMPILETIME,
		    CS1, CS2, CS3, CS4, CS5, CS6, CS7);
    if (TIMERS_ENABLED == TRUE) print_timers();
}
static void evolve(dcomplex u0[NZ][NY][NX], dcomplex u1[NZ][NY][NX],
		   int t, int indexmap[NZ][NY][NX], int d[3]) {
    int i, j, k;
    for (k = 0; k < d[2]; k++) {
	for (j = 0; j < d[1]; j++) {
            for (i = 0; i < d[0]; i++) {
	      crmul(u1[k][j][i], u0[k][j][i], ex[t*indexmap[k][j][i]]);
	    }
	}
    }
}
static void compute_initial_conditions(dcomplex u0[NZ][NY][NX], int d[3]) {
    int k;
    double start, an, dummy;
    start = SEED;
    ipow46(A, (zstart[0]-1)*2*NX*NY + (ystart[0]-1)*2*NX, &an);
    dummy = randlc(&start, an);
