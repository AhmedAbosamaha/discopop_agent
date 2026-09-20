#include "npb-C.h"
#include "globals.h"
#define T_BENCH	1
#define	T_INIT	2
static int is1, is2, is3, ie1, ie2, ie3;
static void setup(int *n1, int *n2, int *n3, int lt);
static void mg3P(double ****u, double ***v, double ****r, double a[4],
		 double c[4], int n1, int n2, int n3, int k);
static void psinv( double ***r, double ***u, int n1, int n2, int n3,
		   double c[4], int k);
static void resid( double ***u, double ***v, double ***r,
		   int n1, int n2, int n3, double a[4], int k );
static void rprj3( double ***r, int m1k, int m2k, int m3k,
		   double ***s, int m1j, int m2j, int m3j, int k );
static void interp( double ***z, int mm1, int mm2, int mm3,
		    double ***u, int n1, int n2, int n3, int k );
static void norm2u3(double ***r, int n1, int n2, int n3,
		    double *rnm2, double *rnmu, int nx, int ny, int nz);
static void rep_nrm(double ***u, int n1, int n2, int n3,
		    char *title, int kk);
static void comm3(double ***u, int n1, int n2, int n3, int kk);
static void zran3(double ***z, int n1, int n2, int n3, int nx, int ny, int k);
static void showall(double ***z, int n1, int n2, int n3);
static double power( double a, int n );
static void bubble( double ten[M][2], int j1[M][2], int j2[M][2],
		    int j3[M][2], int m, int ind );
static void zero3(double ***z, int n1, int n2, int n3);
static void nonzero(double ***z, int n1, int n2, int n3);
int main(int argc, char *argv[]) {
    int k, it;
    double t, tinit, mflops;
    int nthreads = 1;
    double ****u, ***v, ****r;
    double a[4], c[4];
    double rnm2, rnmu;
    double epsilon = 1.0e-8;
    int n1, n2, n3, nit;
    double verify_value;
    boolean verified;
    int i, j, l;
    FILE *fp;
    timer_clear(T_BENCH);
    timer_clear(T_INIT);
    timer_start(T_INIT);
    printf("\n\n NAS Parallel Benchmarks 3.0 structured OpenMP C version"
	   " - MG Benchmark\n\n");
    fp = fopen("mg.input", "r");
    if (fp != NULL) {
	printf(" Reading from input file mg.input\n");
	fscanf(fp, "%d", &lt);
	while(fgetc(fp) != '\n');
	fscanf(fp, "%d%d%d", &nx[lt], &ny[lt], &nz[lt]);
	while(fgetc(fp) != '\n');
	fscanf(fp, "%d", &nit);
	while(fgetc(fp) != '\n');
	for (i = 0; i <= 7; i++) {
	    fscanf(fp, "%d", &debug_vec[i]);
	}
	fclose(fp);
    } else {
	printf(" No input file. Using compiled defaults\n");
	lt = LT_DEFAULT;
	nit = NIT_DEFAULT;
	nx[lt] = NX_DEFAULT;
	ny[lt] = NY_DEFAULT;
	nz[lt] = NZ_DEFAULT;
	for (i = 0; i <= 7; i++) {
	    debug_vec[i] = DEBUG_DEFAULT;
	}
    }
    if ( (nx[lt] != ny[lt]) || (nx[lt] != nz[lt]) ) {
	Class = 'U';
    } else if( nx[lt] == 32 && nit == 4 ) {
	Class = 'S';
    } else if( nx[lt] == 64 && nit == 40 ) {
	Class = 'W';
    } else if( nx[lt] == 256 && nit == 20 ) {
	Class = 'B';
    } else if( nx[lt] == 512 && nit == 20 ) {
	Class = 'C';
    } else if( nx[lt] == 256 && nit == 4 ) {
	Class = 'A';
    } else {
	Class = 'U';
    }
    a[0] = -8.0/3.0;
    a[1] =  0.0;
    a[2] =  1.0/6.0;
    a[3] =  1.0/12.0;
    if (Class == 'A' || Class == 'S' || Class =='W') {
	c[0] =  -3.0/8.0;
	c[1] =  1.0/32.0;
	c[2] =  -1.0/64.0;
	c[3] =   0.0;
    } else {
	c[0] =  -3.0/17.0;
	c[1] =  1.0/33.0;
	c[2] =  -1.0/61.0;
	c[3] =   0.0;
    }
    lb = 1;
    setup(&n1,&n2,&n3,lt);
    u = (double ****)malloc((lt+1)*sizeof(double ***));
    for (l = lt; l >=1; l--) {
	u[l] = (double ***)malloc(m3[l]*sizeof(double **));
	for (k = 0; k < m3[l]; k++) {
	    u[l][k] = (double **)malloc(m2[l]*sizeof(double *));
	    for (j = 0; j < m2[l]; j++) {
		u[l][k][j] = (double *)malloc(m1[l]*sizeof(double));
	    }
	}
    }
    v = (double ***)malloc(m3[lt]*sizeof(double **));
    for (k = 0; k < m3[lt]; k++) {
	v[k] = (double **)malloc(m2[lt]*sizeof(double *));
	for (j = 0; j < m2[lt]; j++) {
	    v[k][j] = (double *)malloc(m1[lt]*sizeof(double));
	}
    }
    r = (double ****)malloc((lt+1)*sizeof(double ***));
    for (l = lt; l >=1; l--) {
	r[l] = (double ***)malloc(m3[l]*sizeof(double **));
	for (k = 0; k < m3[l]; k++) {
	    r[l][k] = (double **)malloc(m2[l]*sizeof(double *));
	    for (j = 0; j < m2[l]; j++) {
		r[l][k][j] = (double *)malloc(m1[l]*sizeof(double));
	    }
	}
    }
    zero3(u[lt],n1,n2,n3);
    zran3(v,n1,n2,n3,nx[lt],ny[lt],lt);
    norm2u3(v,n1,n2,n3,&rnm2,&rnmu,nx[lt],ny[lt],nz[lt]);
    printf(" Size: %3dx%3dx%3d (class %1c)\n",
	   nx[lt], ny[lt], nz[lt], Class);
    printf(" Iterations: %3d\n", nit);
    resid(u[lt],v,r[lt],n1,n2,n3,a,lt);
    norm2u3(r[lt],n1,n2,n3,&rnm2,&rnmu,nx[lt],ny[lt],nz[lt]);
    mg3P(u,v,r,a,c,n1,n2,n3,lt);
    resid(u[lt],v,r[lt],n1,n2,n3,a,lt);
    setup(&n1,&n2,&n3,lt);
    zero3(u[lt],n1,n2,n3); 
    zran3(v,n1,n2,n3,nx[lt],ny[lt],lt);
    timer_stop(T_INIT);
    timer_start(T_BENCH);
    resid(u[lt],v,r[lt],n1,n2,n3,a,lt);
    norm2u3(r[lt],n1,n2,n3,&rnm2,&rnmu,nx[lt],ny[lt],nz[lt]);
    for ( it = 1; it <= nit; it++) {
	mg3P(u,v,r,a,c,n1,n2,n3,lt);
	resid(u[lt],v,r[lt],n1,n2,n3,a,lt);
    }
    norm2u3(r[lt],n1,n2,n3,&rnm2,&rnmu,nx[lt],ny[lt],nz[lt]);
{   
#if defined(_OPENMP)
  nthreads = omp_get_num_threads();
#endif 
} 
    timer_stop(T_BENCH);
    t = timer_read(T_BENCH);
    tinit = timer_read(T_INIT);
    verified = FALSE;
    verify_value = 0.0;
    printf(" Initialization time: %15.3f seconds\n", tinit);
    printf(" Benchmark completed\n");
    if (Class != 'U') {
	if (Class == 'S') {
            verify_value = 0.530770700573e-04;
	} else if (Class == 'W') {
            verify_value = 0.250391406439e-17;  
	} else if (Class == 'A') {
            verify_value = 0.2433365309e-5;
        } else if (Class == 'B') {
            verify_value = 0.180056440132e-5;
        } else if (Class == 'C') {
            verify_value = 0.570674826298e-06;
	}
	if ( fabs( rnm2 - verify_value ) <= epsilon ) {
            verified = TRUE;
	    printf(" VERIFICATION SUCCESSFUL\n");
	    printf(" L2 Norm is %20.12e\n", rnm2);
	    printf(" Error is   %20.12e\n", rnm2 - verify_value);
	} else {
            verified = FALSE;
	    printf(" VERIFICATION FAILED\n");
	    printf(" L2 Norm is             %20.12e\n", rnm2);
	    printf(" The correct L2 Norm is %20.12e\n", verify_value);
	}
    } else {
	verified = FALSE;
	printf(" Problem size unknown\n");
	printf(" NO VERIFICATION PERFORMED\n");
    }
    if ( t != 0.0 ) {
	int nn = nx[lt]*ny[lt]*nz[lt];
	mflops = 58.*nit*nn*1.0e-6 / t;
    } else {
	mflops = 0.0;
    }
    c_print_results("MG", Class, nx[lt], ny[lt], nz[lt], 
		    nit, nthreads, t, mflops, "          floating point", 
		    verified, NPBVERSION, COMPILETIME,
		    CS1, CS2, CS3, CS4, CS5, CS6, CS7);
}
static void setup(int *n1, int *n2, int *n3, int lt) {
    int k;
    for ( k = lt-1; k >= 1; k--) {
	nx[k] = nx[k+1]/2;
	ny[k] = ny[k+1]/2;
	nz[k] = nz[k+1]/2;
    }
    for (k = 1; k <= lt; k++) {
	m1[k] = nx[k]+2;
	m2[k] = nz[k]+2;
	m3[k] = ny[k]+2;
    }
    is1 = 1;
    ie1 = nx[lt];
    *n1 = nx[lt]+2;
    is2 = 1;
    ie2 = ny[lt];
    *n2 = ny[lt]+2;
    is3 = 1;
    ie3 = nz[lt];
    *n3 = nz[lt]+2;
    if (debug_vec[1] >=  1 ) {
	printf(" in setup, \n");
	printf("  lt  nx  ny  nz  n1  n2  n3 is1 is2 is3 ie1 ie2 ie3\n");
	printf("%4d%4d%4d%4d%4d%4d%4d%4d%4d%4d%4d%4d%4d\n",
	       lt,nx[lt],ny[lt],nz[lt],*n1,*n2,*n3,is1,is2,is3,ie1,ie2,ie3);
    }
}
static void mg3P(double ****u, double ***v, double ****r, double a[4],
		 double c[4], int n1, int n2, int n3, int k) {
    int j;
    for (k = lt; k >= lb+1; k--) {
	j = k-1;
	rprj3(r[k], m1[k], m2[k], m3[k],
	      r[j], m1[j], m2[j], m3[j], k);
    }
    k = lb;
    zero3(u[k], m1[k], m2[k], m3[k]);
    psinv(r[k], u[k], m1[k], m2[k], m3[k], c, k);
    for (k = lb+1; k <= lt-1; k++) {
	j = k-1;
	zero3(u[k], m1[k], m2[k], m3[k]);
	interp(u[j], m1[j], m2[j], m3[j],
	       u[k], m1[k], m2[k], m3[k], k);
	resid(u[k], r[k], r[k], m1[k], m2[k], m3[k], a, k);
	psinv(r[k], u[k], m1[k], m2[k], m3[k], c, k);
    }
    j = lt - 1;
    k = lt;
    interp(u[j], m1[j], m2[j], m3[j], u[lt], n1, n2, n3, k);
    resid(u[lt], v, r[lt], n1, n2, n3, a, k);
    psinv(r[lt], u[lt], n1, n2, n3, c, k);
}
static void psinv( double ***r, double ***u, int n1, int n2, int n3,
		   double c[4], int k) {
    int i3, i2, i1;
    double r1[M], r2[M]; 
    for (i3 = 1; i3 < n3-1; i3++) {
        for (i2 = 1; i2 < n2-1; i2++) {
            for (i1 = 0; i1 < n1; i1++) {
                r1[i1] = r[i3][i2-1][i1] + r[i3][i2+1][i1]
                    + r[i3-1][i2][i1] + r[i3+1][i2][i1];
                r2[i1] = r[i3-1][i2-1][i1] + r[i3-1][i2+1][i1]
                    + r[i3+1][i2-1][i1] + r[i3+1][i2+1][i1];
            }
            for (i1 = 1; i1 < n1-1; i1++) {
                u[i3][i2][i1] = u[i3][i2][i1]
                    + c[0] * r[i3][i2][i1]
                    + c[1] * ( r[i3][i2][i1-1] + r[i3][i2][i1+1]
                               + r1[i1] )
                    + c[2] * ( r2[i1] + r1[i1-1] + r1[i1+1] );
            }
        }
    }
    free(r1);
    free(r2);
} 
    comm3(u,n1,n2,n3,k);
    if (debug_vec[0] >= 1 ) {
	rep_nrm(u,n1,n2,n3,"   psinv",k);
    }
    if ( debug_vec[3] >= k ) {
	showall(u,n1,n2,n3);
    }
}
static void resid( double ***u, double ***v, double ***r,
		   int n1, int n2, int n3, double a[4], int k ) {
int i1,i2,i3;
    for (i3 = 1; i3 < n3-1; i3++) {
        for (i2 = 1; i2 < n2-1; i2++) {
            for (i1 = 0; i1 < n1; i1++) {
                u1[i1] = u[i3][i2-1][i1] + u[i3][i2+1][i1]
                       + u[i3-1][i2][i1] + u[i3+1][i2][i1];
                u2[i1] = u[i3-1][i2-1][i1] + u[i3-1][i2+1][i1]
                       + u[i3+1][i2-1][i1] + u[i3+1][i2+1][i1];
            }
            for (i1 = 1; i1 < n1-1; i1++) {
                r[i3][i2][i1] = v[i3][i2][i1]
                    - a[0] * u[i3][i2][i1]
                    - a[2] * ( u2[i1] + u1[i1-1] + u1[i1+1] )
                    - a[3] * ( u2[i1-1] + u2[i1+1] );
            }
        }
    }
    free(u1);
    free(u2);
} 
    comm3(r,n1,n2,n3,k);
    if (debug_vec[0] >= 1 ) {
        rep_nrm(r,n1,n2,n3,"   resid",k);
    }
    if ( debug_vec[2] >= k ) {
        showall(r,n1,n2,n3);
    }
}
static void rprj3(double ***r, int m1k, int m2k, int m3k,
                  double ***s, int m1j, int m2j, int m3j, int k) {
    int j3, j2, j1, i3, i2, i1, d1, d2, d3;
    double x2, y2;
    d1 = (m1k == 3) ? 2 : 1;
    d2 = (m2k == 3) ? 2 : 1;
    d3 = (m3k == 3) ? 2 : 1;
#pragma omp parallel for private(j2, j1, i3, i2, i1, x2, y2) schedule(dynamic)
for (j3 = 1; j3 < m3j-1; j3++) {
    for (j2 = 1; j2 < m2j-1; j2++) {
        double x1[M], y1[M];  
        double x2, y2;        
        i3 = 2*j3 - d3;
        i2 = 2*j2 - d2;
        for (j1 = 1; j1 < m1j; j1++) {
            i1 = 2*j1 - d1;
            x1[i1] = r[i3+1][i2][i1] + r[i3+1][i2+2][i1]
                   + r[i3][i2+1][i1] + r[i3+2][i2+1][i1];
            y1[i1] = r[i3][i2][i1] + r[i3+2][i2][i1]
                   + r[i3][i2+2][i1] + r[i3+2][i2+2][i1];
        }
        for (j1 = 1; j1 < m1j-1; j1++) {
            i1 = 2*j1 - d1;
            y2 = r[i3][i2][i1+1] + r[i3+2][i2][i1+1]
               + r[i3][i2+2][i1+1] + r[i3+2][i2+2][i1+1];
            x2 = r[i3+1][i2][i1+1] + r[i3+1][i2+2][i1+1]
               + r[i3][i2+1][i1+1] + r[i3+2][i2+1][i1+1];
            s[j3][j2][j1] = 0.5 * r[i3+1][i2+1][i1+1]
                          + 0.25 * (r[i3+1][i2+1][i1] + r[i3+1][i2+1][i1+2] + x2)
                          + 0.125 * (x1[i1] + x1[i1+2] + y2)
                          + 0.0625 * (y1[i1] + y1[i1+2]);
        }
    }
}
    comm3(s, m1j, m2j, m3j, k-1);
    if (debug_vec[0] >= 1) {
        rep_nrm(s, m1j, m2j, m3j, "   rprj3", k-1);
    }
    if (debug_vec[4] >= k) {
        showall(s, m1j, m2j, m3j);
    }
}
static void interp( double ***z, int mm1, int mm2, int mm3,
		    double ***u, int n1, int n2, int n3, int k ) {
    int i3, i2, i1, d1, d2, d3, t1, t2, t3;
#pragma omp parallel
{
    double *z1 = (double*)malloc(mm1 * sizeof(double));
    double *z2 = (double*)malloc(mm1 * sizeof(double));
    double *z3 = (double*)malloc(mm1 * sizeof(double));
    if ( n1 != 3 && n2 != 3 && n3 != 3 ) {
#pragma omp for private(i1, i2, i3) schedule(static)
	for (i3 = 0; i3 < mm3-1; i3++) {
            for (i2 = 0; i2 < mm2-1; i2++) {
		for (i1 = 0; i1 < mm1; i1++) {
		    z1[i1] = z[i3][i2+1][i1] + z[i3][i2][i1];
		    z2[i1] = z[i3+1][i2][i1] + z[i3][i2][i1];
		    z3[i1] = z[i3+1][i2+1][i1] + z[i3+1][i2][i1] + z1[i1];
		}
		for (i1 = 0; i1 < mm1-1; i1++) {
		    u[2*i3][2*i2][2*i1] = u[2*i3][2*i2][2*i1]
			+z[i3][i2][i1];
		    u[2*i3][2*i2][2*i1+1] = u[2*i3][2*i2][2*i1+1]
			+0.5*(z[i3][i2][i1+1]+z[i3][i2][i1]);
		}
		for (i1 = 0; i1 < mm1-1; i1++) {
		    u[2*i3][2*i2+1][2*i1] = u[2*i3][2*i2+1][2*i1]
			+0.5 * z1[i1];
		    u[2*i3][2*i2+1][2*i1+1] = u[2*i3][2*i2+1][2*i1+1]
			+0.25*( z1[i1] + z1[i1+1] );
		}
		for (i1 = 0; i1 < mm1-1; i1++) {
		    u[2*i3+1][2*i2][2*i1] = u[2*i3+1][2*i2][2*i1]
			+0.5 * z2[i1];
		    u[2*i3+1][2*i2][2*i1+1] = u[2*i3+1][2*i2][2*i1+1]
			+0.25*( z2[i1] + z2[i1+1] );
		}
		for (i1 = 0; i1 < mm1-1; i1++) {
		    u[2*i3+1][2*i2+1][2*i1] = u[2*i3+1][2*i2+1][2*i1]
			+0.25* z3[i1];
		    u[2*i3+1][2*i2+1][2*i1+1] = u[2*i3+1][2*i2+1][2*i1+1]
			+0.125*( z3[i1] + z3[i1+1] );
		}
	    }
	}
    } else {
	if (n1 == 3) {
            d1 = 2;
            t1 = 1;
	} else {
            d1 = 1;
            t1 = 0;
	}
	if (n2 == 3) {
            d2 = 2;
            t2 = 1;
	} else {
            d2 = 1;
            t2 = 0;
	}
	if (n3 == 3) {
            d3 = 2;
            t3 = 1;
	} else {
            d3 = 1;
            t3 = 0;
	}
    {
#pragma omp for private(i1, i2, i3) schedule(static)
	for ( i3 = d3; i3 <= mm3-1; i3++) {
            for ( i2 = d2; i2 <= mm2-1; i2++) {
		for ( i1 = d1; i1 <= mm1-1; i1++) {
		    u[2*i3-d3-1][2*i2-d2-1][2*i1-d1-1] =
			u[2*i3-d3-1][2*i2-d2-1][2*i1-d1-1]
			+z[i3-1][i2-1][i1-1];
		}
		for ( i1 = 1; i1 <= mm1-1; i1++) {
		    u[2*i3-d3-1][2*i2-d2-1][2*i1-t1-1] =
			u[2*i3-d3-1][2*i2-d2-1][2*i1-t1-1]
			+0.5*(z[i3-1][i2-1][i1]+z[i3-1][i2-1][i1-1]);
		}
	    }
            for ( i2 = 1; i2 <= mm2-1; i2++) {
		for ( i1 = d1; i1 <= mm1-1; i1++) {
		    u[2*i3-d3-1][2*i2-t2-1][2*i1-d1-1] =
			u[2*i3-d3-1][2*i2-t2-1][2*i1-d1-1]
			+0.5*(z[i3-1][i2][i1-1]+z[i3-1][i2-1][i1-1]);
		}
		for ( i1 = 1; i1 <= mm1-1; i1++) {
		    u[2*i3-d3-1][2*i2-t2-1][2*i1-t1-1] =
			u[2*i3-d3-1][2*i2-t2-1][2*i1-t1-1]
			+0.25*(z[i3-1][i2][i1]+z[i3-1][i2-1][i1]
			       +z[i3-1][i2][i1-1]+z[i3-1][i2-1][i1-1]);
		}
	    }
	}
#pragma omp for private(i1, i2, i3) schedule(static)
	for ( i3 = 1; i3 <= mm3-1; i3++) {
            for ( i2 = d2; i2 <= mm2-1; i2++) {
		for ( i1 = d1; i1 <= mm1-1; i1++) {
		    u[2*i3-t3-1][2*i2-d2-1][2*i1-d1-1] =
			u[2*i3-t3-1][2*i2-d2-1][2*i1-d1-1]
			+0.5*(z[i3][i2-1][i1-1]+z[i3-1][i2-1][i1-1]);
		}
		for ( i1 = 1; i1 <= mm1-1; i1++) {
		    u[2*i3-t3-1][2*i2-d2-1][2*i1-t1-1] =
			u[2*i3-t3-1][2*i2-d2-1][2*i1-t1-1]
			+0.25*(z[i3][i2-1][i1]+z[i3][i2-1][i1-1]
			       +z[i3-1][i2-1][i1]+z[i3-1][i2-1][i1-1]);
		}
	    }
	    for ( i2 = 1; i2 <= mm2-1; i2++) {
		for ( i1 = d1; i1 <= mm1-1; i1++) {
		    u[2*i3-t3-1][2*i2-t2-1][2*i1-d1-1] =
			u[2*i3-t3-1][2*i2-t2-1][2*i1-d1-1]
			+0.25*(z[i3][i2][i1-1]+z[i3][i2-1][i1-1]
			       +z[i3-1][i2][i1-1]+z[i3-1][i2-1][i1-1]);
		}
		for ( i1 = 1; i1 <= mm1-1; i1++) {
		    u[2*i3-t3-1][2*i2-t2-1][2*i1-t1-1] =
			u[2*i3-t3-1][2*i2-t2-1][2*i1-t1-1]
			+0.125*(z[i3][i2][i1]+z[i3][i2-1][i1]
				+z[i3][i2][i1-1]+z[i3][i2-1][i1-1]
				+z[i3-1][i2][i1]+z[i3-1][i2-1][i1]
				+z[i3-1][i2][i1-1]+z[i3-1][i2-1][i1-1]);
		}
	    }
	}
    }
    free(z1);
    free(z2);
    free(z3);
    }
}
    if (debug_vec[0] >= 1 ) {
	rep_nrm(z,mm1,mm2,mm3,"z: inter",k-1);
	rep_nrm(u,n1,n2,n3,"u: inter",k);
    }
    if ( debug_vec[5] >= k ) {
	showall(z,mm1,mm2,mm3);
	showall(u,n1,n2,n3);
    }
}
static void norm2u3(double ***r, int n1, int n2, int n3,
		    double *rnm2, double *rnmu, int nx, int ny, int nz) {
    double s = 0.0;
    int i3, i2, i1, n;
    double a = 0.0, tmp = 0.0;
    n = nx*ny*nz;
    for (i3 = 0;i3 < n3; i3++) {
	for (i2 = 0; i2 < n2; i2++) {
            for (i1 = 0; i1 < n1; i1++) {
		z[i3][i2][i1] = 0.0;
	    }
	}
    }
}