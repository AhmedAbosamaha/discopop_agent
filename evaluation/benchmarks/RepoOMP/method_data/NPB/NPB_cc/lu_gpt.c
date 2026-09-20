#include "npb-C.h"
#include "applu.h"
#include <omp.h>

#if defined(_OPENMP)
static boolean flag[ISIZ1/2*2+1];
#endif 
static void blts (int nx, int ny, int nz, int k,
		  double omega,
		  double v[ISIZ1][ISIZ2/2*2+1][ISIZ3/2*2+1][5],
		  double ldz[ISIZ1][ISIZ2][5][5],
		  double ldy[ISIZ1][ISIZ2][5][5],
		  double ldx[ISIZ1][ISIZ2][5][5],
		  double d[ISIZ1][ISIZ2][5][5],
		  int ist, int iend, int jst, int jend,
		  int nx0, int ny0 );
static void buts(int nx, int ny, int nz, int k,
		 double omega,
		 double v[ISIZ1][ISIZ2/2*2+1][ISIZ3/2*2+1][5],
		 double tv[ISIZ1][ISIZ2][5],
		 double d[ISIZ1][ISIZ2][5][5],
		 double udx[ISIZ1][ISIZ2][5][5],
		 double udy[ISIZ1][ISIZ2][5][5],
		 double udz[ISIZ1][ISIZ2][5][5],
		 int ist, int iend, int jst, int jend,
		 int nx0, int ny0 );
static void domain(void);
static void erhs(void) {
	
	int i, j, k, m;
	double tmp;
	for (i = 0; i < ISIZ1; i++) {
		for (j = 0; j < ISIZ2; j++) {
			for (k = 0; k < ISIZ3; k++) {
				for (m = 0; m < 5; m++) {
					tmp = 0.0; 
				}
			}
		}
	}
}
static void error(void);
static void exact( int i, int j, int k, double u000ijk[5] );
static void jacld(int k);
static void jacu(int k);
static void l2norm (int nx0, int ny0, int nz0,
			int ist, int iend,
			int jst, int jend,
			double v[ISIZ1][ISIZ2/2*2+1][ISIZ3/2*2+1][5],
			double sum[5]);
static void pintgr(void);
static void read_input(void);
static void rhs(void);
static void setbv(void);
static void setcoeff(void);
static void setiv(void);
static void ssor(void);
static void verify(double xcr[5], double xce[5], double xci,
		   char *class, boolean *verified);


static void domain(void) {
  
}

static void error(void) {
  
}

static void pintgr(void) {
  
}

static void read_input(void) {
  
}

static void setbv(void) {
  
}

static void setcoeff(void) {
  
}

static void setiv(void) {
  
}

static void ssor(void) {
  
}

static void verify(double xcr[5], double xce[5], double xci, char *class, boolean *verified) {
  
}
int main(int argc, char **argv) {
  char class;
  boolean verified;
  double mflops;
  int nthreads = 1;
  read_input();
  domain();
  setcoeff();
  setbv();
  setiv();
  erhs();
{  
#if defined(_OPENMP)  
  nthreads = omp_get_num_threads();
#endif   
}
  ssor();
  error();
  pintgr();
  verify ( rsdnm, errnm, frc, &class, &verified );
  mflops = (double)itmax*(1984.77*(double)nx0
			 *(double)ny0
			 *(double)nz0
			 -10923.3*pow2((double)( nx0+ny0+nz0 )/3.0)
			 +27770.9* (double)( nx0+ny0+nz0 )/3.0
			 -144010.0)
    / (maxtime*1000000.0);
  c_print_results("LU", class, nx0,
		  ny0, nz0, itmax, nthreads,
		  maxtime, mflops, "          floating point", verified, 
		  NPBVERSION, COMPILETIME, CS1, CS2, CS3, CS4, CS5, CS6, 
		  "(none)");
}
static void blts (int nx, int ny, int nz, int k,
		  double omega,
		  double v[ISIZ1][ISIZ2/2*2+1][ISIZ3/2*2+1][5],
		  double ldz[ISIZ1][ISIZ2][5][5],
		  double ldy[ISIZ1][ISIZ2][5][5],
		  double ldx[ISIZ1][ISIZ2][5][5],
		  double d[ISIZ1][ISIZ2][5][5],
		  int ist, int iend, int jst, int jend,
		  int nx0, int ny0 ) {
  int i, j, m;
  double tmp, tmp1;
  double tmat[5][5];
  for (i = ist; i <= iend; i++) {
    for (j = jst; j <= jend; j++) {
      for (m = 0; m < 5; m++) {
	v[i][j][k][m] = v[i][j][k][m]
	  - omega * (  ldz[i][j][m][0] * v[i][j][k-1][0]
		       + ldz[i][j][m][1] * v[i][j][k-1][1]
		       + ldz[i][j][m][2] * v[i][j][k-1][2]
		       + ldz[i][j][m][3] * v[i][j][k-1][3]
		       + ldz[i][j][m][4] * v[i][j][k-1][4]  );
      }
    }
  }
  for (i = ist; i <= iend; i++) {
#if defined(_OPENMP)      
    if (i != ist) {
	while (flag[i-1] == 0) {
	    ;
	}
    }
    if (i != iend) {
	while (flag[i] == 1) {
	    ;
	}
    }
#endif 
    for (j = jst; j <= jend; j++) {
      for (m = 0; m < 5; m++) {
	v[i][j][k][m] = v[i][j][k][m]
	  - omega * ( ldy[i][j][m][0] * v[i][j-1][k][0]
		      + ldx[i][j][m][0] * v[i-1][j][k][0]
		      + ldy[i][j][m][1] * v[i][j-1][k][1]
		      + ldx[i][j][m][1] * v[i-1][j][k][1]
		      + ldy[i][j][m][2] * v[i][j-1][k][2]
		      + ldx[i][j][m][2] * v[i-1][j][k][2]
		      + ldy[i][j][m][3] * v[i][j-1][k][3]
		      + ldx[i][j][m][3] * v[i-1][j][k][3]
		      + ldy[i][j][m][4] * v[i][j-1][k][4]
		      + ldx[i][j][m][4] * v[i-1][j][k][4] );
      }
      for (m = 0; m < 5; m++) {
	tmat[m][0] = d[i][j][m][0];
	tmat[m][1] = d[i][j][m][1];
	tmat[m][2] = d[i][j][m][2];
	tmat[m][3] = d[i][j][m][3];
	tmat[m][4] = d[i][j][m][4];
      }
      tmp1 = 1.0 / tmat[0][0];
      tmp = tmp1 * tmat[1][0];
      tmat[1][1] =  tmat[1][1]
	- tmp * tmat[0][1];
      tmat[1][2] =  tmat[1][2]
	- tmp * tmat[0][2];
      tmat[1][3] =  tmat[1][3]
	- tmp * tmat[0][3];
      tmat[1][4] =  tmat[1][4]
	- tmp * tmat[0][4];
      v[i][j][k][1] = v[i][j][k][1]
	- v[i][j][k][0] * tmp;
      tmp = tmp1 * tmat[2][0];
      tmat[2][1] =  tmat[2][1]
	- tmp * tmat[0][1];
      tmat[2][2] =  tmat[2][2]
	- tmp * tmat[0][2];
      tmat[2][3] =  tmat[2][3]
	- tmp * tmat[0][3];
      tmat[2][4] =  tmat[2][4]
	- tmp * tmat[0][4];
      v[i][j][k][2] = v[i][j][k][2]
	- v[i][j][k][0] * tmp;
      tmp = tmp1 * tmat[3][0];
      tmat[3][1] =  tmat[3][1]
	- tmp * tmat[0][1];
      tmat[3][2] =  tmat[3][2]
	- tmp * tmat[0][2];
      tmat[3][3] =  tmat[3][3]
	- tmp * tmat[0][3];
      tmat[3][4] =  tmat[3][4]
	- tmp * tmat[0][4];
      v[i][j][k][3] = v[i][j][k][3]
	- v[i][j][k][0] * tmp;
      tmp = tmp1 * tmat[4][0];
      tmat[4][1] =  tmat[4][1]
	- tmp * tmat[0][1];
      tmat[4][2] =  tmat[4][2]
	- tmp * tmat[0][2];
      tmat[4][3] =  tmat[4][3]
	- tmp * tmat[0][3];
      tmat[4][4] =  tmat[4][4]
	- tmp * tmat[0][4];
      v[i][j][k][4] = v[i][j][k][4]
	- v[i][j][k][0] * tmp;
      tmp1 = 1.0 / tmat[ 1][1];
      tmp = tmp1 * tmat[ 2][1];
      tmat[2][2] =  tmat[2][2]
	- tmp * tmat[1][2];
      tmat[2][3] =  tmat[2][3]
	- tmp * tmat[1][3];
      tmat[2][4] =  tmat[2][4]
	- tmp * tmat[1][4];
      v[i][j][k][2] = v[i][j][k][2]
	- v[i][j][k][1] * tmp;
      tmp = tmp1 * tmat[3][1];
      tmat[3][2] =  tmat[3][2]
	- tmp * tmat[1][2];
      tmat[3][3] =  tmat[3][3]
	- tmp * tmat[1][3];
      tmat[3][4] =  tmat[3][4]
	- tmp * tmat[1][4];
      v[i][j][k][3] = v[i][j][k][3]
	- v[i][j][k][1] * tmp;
      tmp = tmp1 * tmat[4][1];
      tmat[4][2] =  tmat[4][2]
	- tmp * tmat[1][2];
      tmat[4][3] =  tmat[4][3]
	- tmp * tmat[1][3];
      tmat[4][4] =  tmat[4][4]
	- tmp * tmat[1][4];
      v[i][j][k][4] = v[i][j][k][4]
	- v[i][j][k][1] * tmp;
      tmp1 = 1.0 / tmat[2][2];
      tmp = tmp1 * tmat[3][2];
      tmat[3][3] =  tmat[3][3]
	- tmp * tmat[2][3];
      tmat[3][4] =  tmat[3][4]
	- tmp * tmat[2][4];
      v[i][j][k][3] = v[i][j][k][3]
        - v[i][j][k][2] * tmp;
      tmp = tmp1 * tmat[4][2];
      tmat[4][3] =  tmat[4][3]
	- tmp * tmat[2][3];
      tmat[4][4] =  tmat[4][4]
	- tmp * tmat[2][4];
      v[i][j][k][4] = v[i][j][k][4]
	- v[i][j][k][2] * tmp;
      tmp1 = 1.0 / tmat[3][3];
      tmp = tmp1 * tmat[4][3];
      tmat[4][4] =  tmat[4][4]
	- tmp * tmat[3][4];
      v[i][j][k][4] = v[i][j][k][4]
	- v[i][j][k][3] * tmp;
      v[i][j][k][4] = v[i][j][k][4]
	/ tmat[4][4];
      v[i][j][k][3] = v[i][j][k][3]
	- tmat[3][4] * v[i][j][k][4];
      v[i][j][k][3] = v[i][j][k][3]
	/ tmat[3][3];
      v[i][j][k][2] = v[i][j][k][2]
	- tmat[2][3] * v[i][j][k][3]
	- tmat[2][4] * v[i][j][k][4];
      v[i][j][k][2] = v[i][j][k][2]
	/ tmat[2][2];
      v[i][j][k][1] = v[i][j][k][1]
	- tmat[1][2] * v[i][j][k][2]
	- tmat[1][3] * v[i][j][k][3]
	- tmat[1][4] * v[i][j][k][4];
      v[i][j][k][1] = v[i][j][k][1]
	/ tmat[1][1];
      v[i][j][k][0] = v[i][j][k][0]
	- tmat[0][1] * v[i][j][k][1]
	- tmat[0][2] * v[i][j][k][2]
	- tmat[0][3] * v[i][j][k][3]
	- tmat[0][4] * v[i][j][k][4];
      v[i][j][k][0] = v[i][j][k][0]
	/ tmat[0][0];
    }
#if defined(_OPENMP)    
    if (i != ist) flag[i-1] = 0;
    if (i != iend) flag[i] = 1;
#endif     
  }
}
static void buts(int nx, int ny, int nz, int k,
		 double omega,
		 double v[ISIZ1][ISIZ2/2*2+1][ISIZ3/2*2+1][5],
		 double tv[ISIZ1][ISIZ2][5],
		 double d[ISIZ1][ISIZ2][5][5],
		 double udx[ISIZ1][ISIZ2][5][5],
		 double udy[ISIZ1][ISIZ2][5][5],
		 double udz[ISIZ1][ISIZ2][5][5],
		 int ist, int iend, int jst, int jend,
		 int nx0, int ny0 ) {
  int i, j, m;
  double tmp, tmp1;
  double tmat[5][5];
  for (i = iend; i >= ist; i--) {
	for (j = jend; j >= jst; j--) {
		for (m = 0; m < 5; m++) {
			tv[i][j][m] = tv[i][j][m]
			  + omega * ( udy[i][j][m][0] * v[i][j+1][k][0]
						  + udx[i][j][m][0] * v[i+1][j][k][0]
						  + udy[i][j][m][1] * v[i][j+1][k][1]
						  + udx[i][j][m][1] * v[i+1][j][k][1]
						  + udy[i][j][m][2] * v[i][j+1][k][2]
						  + udx[i][j][m][2] * v[i+1][j][k][2]
						  + udy[i][j][m][3] * v[i][j+1][k][3]
						  + udx[i][j][m][3] * v[i+1][j][k][3]
						  + udy[i][j][m][4] * v[i][j+1][k][4]
						  + udx[i][j][m][4] * v[i+1][j][k][4] );
		}
			
		}
				 + udz[i][j][m][1] * v[i][j][k+1][1]
				 + udz[i][j][m][2] * v[i][j][k+1][2]
				 + udz[i][j][m][3] * v[i][j][k+1][3]
				 + udz[i][j][m][4] * v[i][j][k+1][4];
			}
		  }
		}
	  }
	}
	for (i = iend; i >= ist; i--) {
	#if defined(_OPENMP)
	  if (i != iend) {
		while (flag[i+1] == 0) {
		  ;
		}
	  }
	  if (i != ist) {
		while (flag[i] == 1) {
		  ;
		}
	  }
	#endif
	  for (j = jend; j >= jst; j--) {
		for (m = 0; m < 5; m++) {
		  
		}
	  }
	}
```c

for (i = iend; i >= ist; i--) {
  for (j = jend; j >= jst; j--) {
	for (m = 0; m < 5; m++) {
	  tv[i][j][m] = tv[i][j][m]
		+ omega * ( udy[i][j][m][0] * v[i][j+1][k][0]
					+ udx[i][j][m][0] * v[i+1][j][k][0]
					+ udy[i][j][m][1] * v[i][j+1][k][1]
					+ udx[i][j][m][1] * v[i+1][j][k][1]
					+ udy[i][j][m][2] * v[i][j+1][k][2]
					+ udx[i][j][m][2] * v[i+1][j][k][2]
					+ udy[i][j][m][3] * v[i][j+1][k][3]
					+ udx[i][j][m][3] * v[i+1][j][k][3]
					+ udy[i][j][m][4] * v[i][j+1][k][4]
					+ udx[i][j][m][4] * v[i+1][j][k][4]
					+ udz[i][j][m][1] * v[i][j][k+1][1]
					+ udz[i][j][m][2] * v[i][j][k+1][2]
					+ udz[i][j][m][3] * v[i][j][k+1][3]
					+ udz[i][j][m][4] * v[i][j][k+1][4]);
	}
  }
}

#if defined(_OPENMP)
for (i = iend; i >= ist; i--) {
  if (i != iend) {
	while (flag[i+1] == 0) {
	  ;
	}
  }
  if (i != ist) {
	while (flag[i] == 1) {
	  ;
	}
  }
}
#endif
	  tmp1 = 1.0 / tmat[0][0];
	  tmp = tmp1 * tmat[1][0];
	  tmat[1][1] =  tmat[1][1]
	- tmp * tmat[0][1];
	  tmat[1][2] =  tmat[1][2]
	- tmp * tmat[0][2];
	  tmat[1][3] =  tmat[1][3]
	- tmp * tmat[0][3];
	  tmat[1][4] =  tmat[1][4]
	- tmp * tmat[0][4];
	  tv[i][j][1] = tv[i][j][1]
	- tv[i][j][0] * tmp;
	  tmp = tmp1 * tmat[2][0];
	  tmat[2][1] =  tmat[2][1]
	- tmp * tmat[0][1];
	  tmat[2][2] =  tmat[2][2]
	- tmp * tmat[0][2];
	  tmat[2][3] =  tmat[2][3]
	- tmp * tmat[0][3];
	  tmat[2][4] =  tmat[2][4]
	- tmp * tmat[0][4];
	  tv[i][j][2] = tv[i][j][2]
	- tv[i][j][0] * tmp;
	  tmp = tmp1 * tmat[3][0];
	  tmat[3][1] =  tmat[3][1]
	- tmp * tmat[0][1];
	  tmat[3][2] =  tmat[3][2]
	- tmp * tmat[0][2];
	  tmat[3][3] =  tmat[3][3]
	- tmp * tmat[0][3];
	  tmat[3][4] =  tmat[3][4]
	- tmp * tmat[0][4];
	  tv[i][j][3] = tv[i][j][3]
	- tv[i][j][0] * tmp;
	  tmp = tmp1 * tmat[4][0];
	  tmat[4][1] =  tmat[4][1]
	- tmp * tmat[0][1];
	  tmat[4][2] =  tmat[4][2]
	- tmp * tmat[0][2];
	  tmat[4][3] =  tmat[4][3]
	- tmp * tmat[0][3];
	  tmat[4][4] =  tmat[4][4]
	- tmp * tmat[0][4];
	  tv[i][j][4] = tv[i][j][4]
	- tv[i][j][0] * tmp;
	  tmp1 = 1.0 / tmat[ 1][1];
	  tmp = tmp1 * tmat[ 2][1];
	  tmat[2][2] =  tmat[2][2]
	- tmp * tmat[1][2];
	  tmat[2][3] =  tmat[2][3]
	- tmp * tmat[1][3];
	  tmat[2][4] =  tmat[2][4]
	- tmp * tmat[1][4];
	  tv[i][j][2] = tv[i][j][2]
	- tv[i][j][1] * tmp;
	  tmp = tmp1 * tmat[3][1];
	  tmat[3][2] =  tmat[3][2]
	- tmp * tmat[1][2];
	  tmat[3][3] =  tmat[3][3]
	- tmp * tmat[1][3];
	  tmat[3][4] =  tmat[3][4]
	- tmp * tmat[1][4];
	  tv[i][j][3] = tv[i][j][3]
	- tv[i][j][1] * tmp;
	  tmp = tmp1 * tmat[4][1];
	  tmat[4][2] =  tmat[4][2]
	- tmp * tmat[1][2];
	  tmat[4][3] =  tmat[4][3]
	- tmp * tmat[1][3];
	  tmat[4][4] =  tmat[4][4]
	- tmp * tmat[1][4];
	  tv[i][j][4] = tv[i][j][4]
	- tv[i][j][1] * tmp;
	  tmp1 = 1.0 / tmat[2][2];
	  tmp = tmp1 * tmat[3][2];
	  tmat[3][3] =  tmat[3][3]
	- tmp * tmat[2][3];
	  tmat[3][4] =  tmat[3][4]
	- tmp * tmat[2][4];
	  tv[i][j][3] = tv[i][j][3]
		- v[i][j][k][2] * tmp;
	  tmp = tmp1 * tmat[4][2];
	  tmat[4][3] =  tmat[4][3]
	- tmp * tmat[2][3];
	  tmat[4][4] =  tmat[4][4]
	- tmp * tmat[2][4];
	  tv[i][j][4] = tv[i][j][4]
	- v[i][j][k][2] * tmp;
	  tmp1 = 1.0 / tmat[3][3];
	  tmp = tmp1 * tmat[4][3];
	  tmat[4][4] =  tmat[4][4]
	- tmp * tmat[3][4];
	  tv[i][j][4] = tv[i][j][4]
	- v[i][j][k][3] * tmp;
	  tv[i][j][k][4] =
static void erhs(void) {
  int i, j, k, m;
  int iglob, jglob;
  int L1, L2;
  int ist1, iend1;
  int jst1, jend1;
  double  dsspm;
  double  xi, eta, zeta;
  double  q;
  double  u21, u31, u41;
  double  tmp;
  double  u21i, u31i, u41i, u51i;
  double  u21j, u31j, u41j, u51j;
  double  u21k, u31k, u41k, u51k;
  double  u21im1, u31im1, u41im1, u51im1;
  double  u21jm1, u31jm1, u41jm1, u51jm1;
  double  u21km1, u31km1, u41km1, u51km1;
  dsspm = dssp;
  for (i = 0; i < nx; i++) {
    for (j = 0; j < ny; j++) {
      for (k = 0; k < nz; k++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = 0.0;
	}
      }
    }
  }
  for (i = 0; i < nx; i++) {
    iglob = i;
    xi = ( (double)(iglob) ) / ( nx0 - 1 );
    for (j = 0; j < ny; j++) {
      jglob = j;
      eta = ( (double)(jglob) ) / ( ny0 - 1 );
      for (k = 0; k < nz; k++) {
	zeta = ( (double)(k) ) / ( nz - 1 );
	for (m = 0; m < 5; m++) {
	  rsd[i][j][k][m] =  ce[m][0]
	    + ce[m][1] * xi
	    + ce[m][2] * eta
	    + ce[m][3] * zeta
	    + ce[m][4] * xi * xi
	    + ce[m][5] * eta * eta
	    + ce[m][6] * zeta * zeta
	    + ce[m][7] * xi * xi * xi
	    + ce[m][8] * eta * eta * eta
	    + ce[m][9] * zeta * zeta * zeta
	    + ce[m][10] * xi * xi * xi * xi
	    + ce[m][11] * eta * eta * eta * eta
	    + ce[m][12] * zeta * zeta * zeta * zeta;
	}
      }
    }
  }
  L1 = 0;
  L2 = nx-1;
  for (i = L1; i <= L2; i++) {
    for (j = jst; j <= jend; j++) {
      for (k = 1; k < nz - 1; k++) {
	flux[i][j][k][0] = rsd[i][j][k][1];
	u21 = rsd[i][j][k][1] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u21 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][2] = rsd[i][j][k][2] * u21;
	flux[i][j][k][3] = rsd[i][j][k][3] * u21;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u21;
      }
    }
  }
  for (j = jst; j <= jend; j++) {
    for (k = 1; k <= nz - 2; k++) {
      for (i = ist; i <= iend; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - tx2 * ( flux[i+1][j][k][m] - flux[i-1][j][k][m] );
	}
      }
      for (i = ist; i <= L2; i++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21i = tmp * rsd[i][j][k][1];
	u31i = tmp * rsd[i][j][k][2];
	u41i = tmp * rsd[i][j][k][3];
	u51i = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i-1][j][k][0];
	u21im1 = tmp * rsd[i-1][j][k][1];
	u31im1 = tmp * rsd[i-1][j][k][2];
	u41im1 = tmp * rsd[i-1][j][k][3];
	u51im1 = tmp * rsd[i-1][j][k][4];
	flux[i][j][k][1] = (4.0/3.0) * tx3 * 
	  ( u21i - u21im1 );
	flux[i][j][k][2] = tx3 * ( u31i - u31im1 );
	flux[i][j][k][3] = tx3 * ( u41i - u41im1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * tx3 * ( ( u21i * u21i + u31i * u31i + u41i * u41i )
		    - ( u21im1*u21im1 + u31im1*u31im1 + u41im1*u41im1 ) )
	  + (1.0/6.0)
	  * tx3 * ( u21i*u21i - u21im1*u21im1 )
	  + C1 * C5 * tx3 * ( u51i - u51im1 );
      }
      for (i = ist; i <= iend; i++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dx1 * tx1 * (            rsd[i-1][j][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +       	    rsd[i+1][j][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + tx3 * C3 * C4 * ( flux[i+1][j][k][1] - flux[i][j][k][1] )
	  + dx2 * tx1 * (            rsd[i-1][j][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i+1][j][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + tx3 * C3 * C4 * ( flux[i+1][j][k][2] - flux[i][j][k][2] )
	  + dx3 * tx1 * (            rsd[i-1][j][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i+1][j][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + tx3 * C3 * C4 * ( flux[i+1][j][k][3] - flux[i][j][k][3] )
	  + dx4 * tx1 * (            rsd[i-1][j][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i+1][j][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + tx3 * C3 * C4 * ( flux[i+1][j][k][4] - flux[i][j][k][4] )
	  + dx5 * tx1 * (            rsd[i-1][j][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i+1][j][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 2.0 * rsd[i][j][k][3]
				     +           rsd[i][j+1][k][3] );
	frct[i][j][k][4] = frct[i][j][k][4]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][4] - flux[i][j][k][4] )
	  + dy5 * ty1 * (            rsd[i][j-1][k][4]
				     - 2.0 * rsd[i][j][k][4]
				     +           rsd[i][j+1][k][4] );
      }
      for (m = 0; m < 5; m++) {
	frct[1][j][k][m] = frct[1][j][k][m]
	  - dsspm * ( + 5.0 * rsd[1][j][k][m]
		      - 4.0 * rsd[2][j][k][m]
		      +           rsd[3][j][k][m] );
	frct[2][j][k][m] = frct[2][j][k][m]
	  - dsspm * ( - 4.0 * rsd[1][j][k][m]
		      + 6.0 * rsd[2][j][k][m]
		      - 4.0 * rsd[3][j][k][m]
		      +           rsd[4][j][k][m] );
      }
      ist1 = 3;
      iend1 = nx - 4;
      for (i = ist1; i <=iend1; i++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] = frct[i][j][k][m]
	    - dsspm * (            rsd[i-2][j][k][m]
				   - 4.0 * rsd[i-1][j][k][m]
				   + 6.0 * rsd[i][j][k][m]
				   - 4.0 * rsd[i+1][j][k][m]
				   +           rsd[i+2][j][k][m] );
	}
      }
      for (m = 0; m < 5; m++) {
	frct[nx-3][j][k][m] = frct[nx-3][j][k][m]
	  - dsspm * (             rsd[nx-5][j][k][m]
				  - 4.0 * rsd[nx-4][j][k][m]
				  + 6.0 * rsd[nx-3][j][k][m]
				  - 4.0 * rsd[nx-2][j][k][m]  );
	frct[nx-2][j][k][m] = frct[nx-2][j][k][m]
	  - dsspm * (             rsd[nx-4][j][k][m]
				  - 4.0 * rsd[nx-3][j][k][m]
				  + 5.0 * rsd[nx-2][j][k][m] );
      }
    }
  }
  L1 = 0;
  L2 = ny-1;
  for (i = ist; i <= iend; i++) {
    for (j = L1; j <= L2; j++) {
      for (k = 1; k <= nz - 2; k++) {
	flux[i][j][k][0] = rsd[i][j][k][2];
	u31 = rsd[i][j][k][2] / rsd[i][j][k][0];
	q = 0.50 * (  rsd[i][j][k][1] * rsd[i][j][k][1]
		      + rsd[i][j][k][2] * rsd[i][j][k][2]
		      + rsd[i][j][k][3] * rsd[i][j][k][3] )
	  / rsd[i][j][k][0];
	flux[i][j][k][1] = rsd[i][j][k][1] * u31;
	flux[i][j][k][2] = rsd[i][j][k][2] * u31 + C2 * 
	  ( rsd[i][j][k][4] - q );
	flux[i][j][k][3] = rsd[i][j][k][3] * u31;
	flux[i][j][k][4] = ( C1 * rsd[i][j][k][4] - C2 * q ) * u31;
      }
    }
  }
  for (i = ist; i <= iend; i++) {
    for (k = 1; k <= nz - 2; k++) {
      for (j = jst; j <= jend; j++) {
	for (m = 0; m < 5; m++) {
	  frct[i][j][k][m] =  frct[i][j][k][m]
	    - ty2 * ( flux[i][j+1][k][m] - flux[i][j-1][k][m] );
	}
      }
      for (j = jst; j <= L2; j++) {
	tmp = 1.0 / rsd[i][j][k][0];
	u21j = tmp * rsd[i][j][k][1];
	u31j = tmp * rsd[i][j][k][2];
	u41j = tmp * rsd[i][j][k][3];
	u51j = tmp * rsd[i][j][k][4];
	tmp = 1.0 / rsd[i][j-1][k][0];
	u21jm1 = tmp * rsd[i][j-1][k][1];
	u31jm1 = tmp * rsd[i][j-1][k][2];
	u41jm1 = tmp * rsd[i][j-1][k][3];
	u51jm1 = tmp * rsd[i][j-1][k][4];
	flux[i][j][k][1] = ty3 * ( u21j - u21jm1 );
	flux[i][j][k][2] = (4.0/3.0) * ty3 * (u31j-u31jm1);
	flux[i][j][k][3] = ty3 * ( u41j - u41jm1 );
	flux[i][j][k][4] = 0.50 * ( 1.0 - C1*C5 )
	  * ty3 * (   ( pow2(u21j)   + pow2(u31j)   + pow2(u41j) )
		    - ( pow2(u21jm1) + pow2(u31jm1) + pow2(u41jm1) ) )
	  + (1.0/6.0)
	  * ty3 * ( pow2(u31j) - pow2(u31jm1) )
	  + C1 * C5 * ty3 * ( u51j - u51jm1 );
      }
      for (j = jst; j <= jend; j++) {
	frct[i][j][k][0] = frct[i][j][k][0]
	  + dy1 * ty1 * (            rsd[i][j-1][k][0]
				     - 2.0 * rsd[i][j][k][0]
				     +           rsd[i][j+1][k][0] );
	frct[i][j][k][1] = frct[i][j][k][1]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][1] - flux[i][j][k][1] )
	  + dy2 * ty1 * (            rsd[i][j-1][k][1]
				     - 2.0 * rsd[i][j][k][1]
				     +           rsd[i][j+1][k][1] );
	frct[i][j][k][2] = frct[i][j][k][2]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][2] - flux[i][j][k][2] )
	  + dy3 * ty1 * (            rsd[i][j-1][k][2]
				     - 2.0 * rsd[i][j][k][2]
				     +           rsd[i][j+1][k][2] );
	frct[i][j][k][3] = frct[i][j][k][3]
	  + ty3 * C3 * C4 * ( flux[i][j+1][k][3] - flux[i][j][k][3] )
	  + dy4 * ty1 * (            rsd[i][j-1][k][3]
				     - 