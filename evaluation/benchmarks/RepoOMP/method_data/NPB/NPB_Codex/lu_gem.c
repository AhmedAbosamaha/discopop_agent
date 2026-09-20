#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include "applu.h"







static void blts(int,int,int,int,int,int,double[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5]);
static void buts(int,int,int,int,int,int,double[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5],
                 double[ISIZ2/2*2+1][ISIZ1/2*2+1][5]);
static void domain();
static void erhs();
static void exact(int,int,int,double[5]);
static void jacld(int,int,double[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5]);
static void jacu(int,int,double[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5]);
static void l2norm ( int, int, int, int, int, double[ISIZ2/2*2+1][ISIZ1/2*2+1][5], double[5] );
static void pintgr();
static void read_input();
static void rhs();
static void setbv();
static void setiv();
static void ssor(int);
static void verify(double[5],double[5],double[5],char*,
                   boolean*);


void blts(
  int isiz1, int isiz2, int isiz3,
  int nx0, int ny0, int nz0,
  double a[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double b[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double c[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double d[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double r[ISIZ2/2*2+1][ISIZ1/2*2+1][5]) {

  int i, j, k, m;
  double tmp, tmp1;

  #pragma omp parallel for private(i, j, k, m, tmp, tmp1) schedule(static, 1)
  for (k = 1; k < nz0-1; k++) {
    for (j = 1; j < ny0-1; j++) {
      for (i = 1; i < nx0-1; i++) {
        for (m = 0; m < 5; m++) {
          tmp = r[k][j][i][m];
          tmp1 = d[k][j][i][m][0]*tmp;
          r[k][j][i][m] = tmp1;
        }
      }
    }
  }
}


void buts(
  int isiz1, int isiz2, int isiz3,
  int nx0, int ny0, int nz0,
  double a[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double b[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double c[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double d[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5],
  double r[ISIZ2/2*2+1][ISIZ1/2*2+1][5]) {

  int i, j, k, m;

  #pragma omp parallel for private(i, j, k, m) schedule(static, 1)
  for (k = 1; k < nz0-1; k++) {
    for (j = 1; j < ny0-1; j++) {
      for (i = 1; i < nx0-1; i++) {
        for (m = 0; m < 5; m++) {
          r[k][j][i][m] = r[k][j][i][m] - a[k][j][i-1][m][0] * r[k][j][i-1][m] - b[k][j-1][i][m][0] * r[k][j-1][i][m] - c[k-1][j][i][m][0] * r[k-1][j][i][m];
        }
      }
    }
  }
}


void domain() {

}


void erhs() {
  

  int i, j, k, m;
  double xi, eta, zeta;
  double q;
  double u21, u31, u41;
  double u21_xi, u31_xi, u41_xi, u51_xi;
  double u21_eta, u31_eta, u41_eta, u51_eta;
  double u21_zeta, u31_zeta, u41_zeta, u51_zeta;

  for (k = 0; k < nz; k++) {
    for (j = 0; j < ny; j++) {
      for (i = 0; i < nx; i++) {
        for (m = 0; m < 5; m++) {
          r[k][j][i][m] = 0.0;
        }
      }
    }
  }

  for (k = 0; k < nz; k++) {
    zeta = (double)k / (nz - 1);
    for (j = 0; j < ny; j++) {
      eta = (double)j / (ny - 1);
      for (i = 0; i < nx; i++) {
        xi = (double)i / (nx - 1);
        exact(i, j, k, frc[k][j][i]);

        for (m = 0; m < 5; m++) {
          ue[k][j][i][m] = frc[k][j][i][m];
        }

        u21 = ue[k][j][i][1];
        u31 = ue[k][j][i][2];
        u41 = ue[k][j][i][3];

        u21_xi = 0.0;
        u31_xi = 0.0;
        u41_xi = 0.0;
        u51_xi = 0.0;

        u21_eta = 0.0;
        u31_eta = 0.0;
        u41_eta = 0.0;
        u51_eta = 0.0;

        u21_zeta = 0.0;
        u31_zeta = 0.0;
        u41_zeta = 0.0;
        u51_zeta = 0.0;

        for (m = 0; m < 5; m++) {
          r[k][j][i][m] = frc[k][j][i][m];
        }

        q = 1.0 / (u[k][j][i][0]);

        r[k][j][i][1] = r[k][j][i][1] - (u[k][j][i][1] * u21_xi + u[k][j][i][2] * u21_eta + u[k][j][i][3] * u21_zeta);
        r[k][j][i][2] = r[k][j][i][2] - (u[k][j][i][1] * u31_xi + u[k][j][i][2] * u31_eta + u[k][j][i][3] * u31_zeta);
        r[k][j][i][3] = r[k][j][i][3] - (u[k][j][i][1] * u41_xi + u[k][j][i][2] * u41_eta + u[k][j][i][3] * u41_zeta);
        r[k][j][i][4] = r[k][j][i][4] - (u[k][j][i][1] * u51_xi + u[k][j][i][2] * u51_eta + u[k][j][i][3] * u51_zeta);
      }
    }
  }
}


void exact(int i, int j, int k, double u000[5]) {

  int m;
  double xi, eta, zeta;

  xi = (double)i / (nx - 1);
  eta = (double)j / (ny - 1);
  zeta = (double)k / (nz - 1);

  for (m = 0; m < 5; m++) {
    u000[m] = 1.0 + xi + eta + zeta;
  }
}



void jacld(int j, int k, double a[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5]) {
  

  int i, m, n;

  #pragma omp parallel for private(i, m, n) schedule(static, 1)
  for (i = 1; i < nx - 1; i++) {
    for (m = 0; m < 5; m++) {
      for (n = 0; n < 5; n++) {
        a[k][j][i][m][n] = 0.0;
      }
    }
    for (m = 0; m < 5; m++) {
      a[k][j][i][m][m] = 1.0;
    }
  }
}


void jacu(int j, int k, double a[ISIZ2/2*2+1][ISIZ1/2*2+1][5][5]) {


  int i, m, n;

  #pragma omp parallel for private(i, m, n) schedule(static, 1)
  for (i = 1; i < nx - 1; i++) {
    for (m = 0; m < 5; m++) {
      for (n = 0; n < 5; n++) {
        a[k][j][i][m][n] = 0.0;
      }
    }
    for (m = 0; m < 5; m++) {
      a[k][j][i][m][m] = 1.0;
    }
  }
}


void l2norm ( int ldx, int ldy, int ldz, int nx0, int ny0, double v[ISIZ2/2*2+1][ISIZ1/2*2+1][5], double sum[5] ) {


  int i, j, k, m;
  double rsd[5];

  for (m = 0; m < 5; m++) {
    sum[m] = 0.0;
  }

  for (k = 1; k < ldz-1; k++) {
    for (j = 1; j < ldy-1; j++) {
      for (i = 1; i < ldx-1; i++) {
        for (m = 0; m < 5; m++) {
          rsd[m] = v[k][j][i][m];
          sum[m] = sum[m] + rsd[m]*rsd[m];
        }
      }
    }
  }

  for (m = 0; m < 5; m++) {
    sum[m] = sqrt(sum[m] / ( (nx0-2)*(ny0-2)*(ldz-2) ) );
  }
}


void pintgr() {

}


void read_input() {

}


void rhs() {

}


void setbv() {

}


void setiv() {

}


void ssor(int niter) {

  int i, j, k, m, n, istep;
  double tmp, tmp2;

  for (istep = 0; istep < niter; istep++) {
    
    
    
    for (k = 1; k < nz - 1; k++) {
      for (j = 1; j < ny - 1; j++) {
        for (i = 1; i < nx - 1; i++) {
          for (m = 0; m < 5; m++) {
            tmp = r[k][j][i][m];
            tmp2 = d[k][j][i][m][0] * tmp;
            r[k][j][i][m] = tmp2;
          }
        }
      }
    }

    
    
    
    for (k = nz - 2; k >= 1; k--) {
      for (j = ny - 2; j >= 1; j--) {
        for (i = nx - 2; i >= 1; i--) {
          for (m = 0; m < 5; m++) {
            r[k][j][i][m] = r[k][j][i][m] - a[k][j][i-1][m][0] * r[k][j][i-1][m] - b[k][j-1][i][m][0] * r[k][j-1][i][m] - c[k-1][j][i][m][0] * r[k-1][j][i][m];
          }
        }
      }
    }
  }
}


void verify(double xcr[5], double xce[5], double xci[5], char* class, boolean* verified) {

}
