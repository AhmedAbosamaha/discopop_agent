#include "npb-C.h"
#include "npbparams.h"
#define	NZ	NA*(NONZER+1)*(NONZER+1)+NA*(NONZER+2)
static int naa;
static int nzz;
static int firstrow;
static int lastrow;
static int firstcol;
static int lastcol;
static int colidx[NZ+1];	
static int rowstr[NA+1+1];	
static int iv[2*NA+1+1];	
static int arow[NZ+1];		
static int acol[NZ+1];		
static double v[NA+1+1];	
static double aelt[NZ+1];	
static double a[NZ+1];		
static double x[NA+2+1];	
static double z[NA+2+1];	
static double p[NA+2+1];	
static double q[NA+2+1];	
static double r[NA+2+1];	
static double amult;
static double tran;
static void conj_grad (int colidx[], int rowstr[], double x[], double z[],
		       double a[], double p[], double q[], double r[],
		       double *rnorm);
static void makea(int n, int nz, double a[], int colidx[], int rowstr[],
		  int nonzer, int firstrow, int lastrow, int firstcol,
		  int lastcol, double rcond, int arow[], int acol[],
		  double aelt[], double v[], int iv[], double shift );
static void sparse(double a[], int colidx[], int rowstr[], int n,
		   int arow[], int acol[], double aelt[],
		   int firstrow, int lastrow,
		   double x[], boolean mark[], int nzloc[], int nnza);
static void sprnvc(int n, int nz, double v[], int iv[], int nzloc[],
		   int mark[]);
static int icnvrt(double x, int ipwr2);
static void vecset(int n, double v[], int iv[], int *nzv, int i, double val);
int main(int argc, char **argv) {
    int	i, j, k, it;
    int nthreads = 1;
    double zeta;
    double rnorm;
    double norm_temp11;
    double norm_temp12;
    double t, mflops;
    char class;
    boolean verified;
    double zeta_verify_value, epsilon;
    firstrow = 1;
    lastrow  = NA;
    firstcol = 1;
    lastcol  = NA;
    if (NA == 1400 && NONZER == 7 && NITER == 15 && SHIFT == 10.0) {
	class = 'S';
	zeta_verify_value = 8.5971775078648;
    } else if (NA == 7000 && NONZER == 8 && NITER == 15 && SHIFT == 12.0) {
	class = 'W';
	zeta_verify_value = 10.362595087124;
    } else if (NA == 14000 && NONZER == 11 && NITER == 15 && SHIFT == 20.0) {
	class = 'A';
	zeta_verify_value = 17.130235054029;
    } else if (NA == 75000 && NONZER == 13 && NITER == 75 && SHIFT == 60.0) {
	class = 'B';
	zeta_verify_value = 22.712745482631;
    } else if (NA == 150000 && NONZER == 15 && NITER == 75 && SHIFT == 110.0) {
	class = 'C';
	zeta_verify_value = 28.973605592845;
    } else {
	class = 'U';
    }
    printf("\n\n NAS Parallel Benchmarks 3.0 structured OpenMP C version"
	   " - CG Benchmark\n");
    printf(" Size: %10d\n", NA);
    printf(" Iterations: %5d\n", NITER);
    naa = NA;
    nzz = NZ;
    tran    = 314159265.0;
    amult   = 1220703125.0;
    zeta    = randlc( &tran, amult );
    makea(naa, nzz, a, colidx, rowstr, NONZER,
	  firstrow, lastrow, firstcol, lastcol, 
	  RCOND, arow, acol, aelt, v, iv, SHIFT);
{	
    for (j = 1; j <= lastrow - firstrow + 1; j++) {
	for (k = rowstr[j]; k < rowstr[j+1]; k++) {
            colidx[k] = colidx[k] - firstcol + 1;
	}
    }
    for (i = 1; i <= NA+1; i++) {
	x[i] = 1.0;
    }
      for (j = 1; j <= lastcol-firstcol+1; j++) {
         q[j] = 0.0;
         z[j] = 0.0;
         r[j] = 0.0;
         p[j] = 0.0;
      }
}
    zeta  = 0.0;
    for (it = 1; it <= 1; it++) {
	conj_grad (colidx, rowstr, x, z, a, p, q, r, &rnorm);
	norm_temp11 = 0.0;
	norm_temp12 = 0.0;
	for (j = 1; j <= lastcol-firstcol+1; j++) {
            norm_temp11 = norm_temp11 + x[j]*z[j];
            norm_temp12 = norm_temp12 + z[j]*z[j];
	}
	norm_temp12 = 1.0 / sqrt( norm_temp12 );
	for (j = 1; j <= lastcol-firstcol+1; j++) {
            x[j] = norm_temp12*z[j];
	}
    } 
    for (i = 1; i <= NA+1; i++) {
         x[i] = 1.0;
    }  
    zeta  = 0.0;
    timer_clear( 1 );
    timer_start( 1 );
    for (it = 1; it <= NITER; it++) {
	conj_grad(colidx, rowstr, x, z, a, p, q, r, &rnorm);
	norm_temp11 = 0.0;
	norm_temp12 = 0.0;
	for (j = 1; j <= lastcol-firstcol+1; j++) {
            norm_temp11 = norm_temp11 + x[j]*z[j];
            norm_temp12 = norm_temp12 + z[j]*z[j];
	}
	norm_temp12 = 1.0 / sqrt( norm_temp12 );
	zeta = SHIFT + 1.0 / norm_temp11;
	if( it == 1 ) {
	  printf("   iteration           ||r||                 zeta\n");
	}
	printf("    %5d       %20.14e%20.13e\n", it, rnorm, zeta);
	for (j = 1; j <= lastcol-firstcol+1; j++) {
            x[j] = norm_temp12*z[j];
	}
    } 
{
#if defined(_OPENMP)
    nthreads = omp_get_num_threads();
#endif 
} 
    timer_stop( 1 );
    t = timer_read( 1 );
    printf(" Benchmark completed\n");
    epsilon = 1.0e-10;
    if (class != 'U') {
	if (fabs(zeta - zeta_verify_value) <= epsilon) {
            verified = TRUE;
	    printf(" VERIFICATION SUCCESSFUL\n");
	    printf(" Zeta is    %20.12e\n", zeta);
	    printf(" Error is   %20.12e\n", zeta - zeta_verify_value);
	} else {
            verified = FALSE;
	    printf(" VERIFICATION FAILED\n");
	    printf(" Zeta                %20.12e\n", zeta);
	    printf(" The correct zeta is %20.12e\n", zeta_verify_value);
	}
    } else {
	verified = FALSE;
	printf(" Problem size unknown\n");
	printf(" NO VERIFICATION PERFORMED\n");
    }
    if ( t != 0.0 ) {
	mflops = (2.0*NITER*NA)
	    * (3.0+(NONZER*(NONZER+1)) + 25.0*(5.0+(NONZER*(NONZER+1))) + 3.0 )
	    / t / 1000000.0;
    } else {
	mflops = 0.0;
    }
    c_print_results("CG", class, NA, 0, 0, NITER, nthreads, t, 
		    mflops, "          floating point", 
		    verified, NPBVERSION, COMPILETIME,
		    CS1, CS2, CS3, CS4, CS5, CS6, CS7);
}
static void conj_grad (
    int colidx[],	
    int rowstr[],	
    double x[],		
    double z[],		
    double a[],		
    double p[],		
    double q[],		
    double r[],		
    double *rnorm )
{
    static int callcount = 0;
    double d, sum, rho, rho0, alpha, beta;
    int i, j, k;
    int cgit, cgitmax = 25;
    rho = 0.0;
    for (j = 1; j <= naa+1; j++) {
        q[j] = 0.0;
        z[j] = 0.0;
        r[j] = x[j];
        p[j] = r[j];
    }

