#include "npb-C.h"
#include "header.h"
static void add(void);
static void adi(void);
static void error_norm(double rms[5]);
static void rhs_norm(double rms[5]);
static void exact_rhs(void);
static void exact_solution(double xi, double eta, double zeta,
			   double dtemp[5]);
static void initialize(void);
static void lhsinit(void);
static void lhsx(void);
static void lhsy(void);
static void lhsz(void);
static void ninvr(void);
static void pinvr(void);
static void compute_rhs(void);
static void set_constants(void);
static void txinvr(void);
static void tzetar(void);
static void verify(int no_time_steps, char *class, boolean *verified);
static void x_solve(void);
static void y_solve(void);
static void z_solve(void);
int main(int argc, char **argv) {
  int niter, step;
  double mflops, tmax;
  int nthreads = 1;
  boolean verified;
  char class;
  FILE *fp;
  printf("\n\n NAS Parallel Benchmarks 3.0 structured OpenMP C version"
	 " - SP Benchmark\n\n");
  fp = fopen("inputsp.data", "r");
  if (fp != NULL) {
      printf(" Reading from input file inputsp.data\n");
      fscanf(fp, "%d", &niter);
      while (fgetc(fp) != '\n');
      fscanf(fp, "%lf", &dt);
      while (fgetc(fp) != '\n');
      fscanf(fp, "%d%d%d",
	     &grid_points[0], &grid_points[1], &grid_points[2]);
      fclose(fp);
  } else {
      printf(" No input file inputsp.data. Using compiled defaults");
      niter = NITER_DEFAULT;
      dt = DT_DEFAULT;
      grid_points[0] = PROBLEM_SIZE;
      grid_points[1] = PROBLEM_SIZE;
      grid_points[2] = PROBLEM_SIZE;
  }
  printf(" Size: %3dx%3dx%3d\n",
	 grid_points[0], grid_points[1], grid_points[2]);
  printf(" Iterations: %3d   dt: %10.6f\n", niter, dt);
  if ( (grid_points[0] > IMAX) ||
       (grid_points[1] > JMAX) ||
       (grid_points[2] > KMAX) ) {
    printf("%d, %d, %d\n", grid_points[0], grid_points[1], grid_points[2]);
    printf(" Problem size too big for compiled array sizes\n");
    exit(1);
  }
  set_constants();
  initialize();
  lhsinit();
  exact_rhs();
    adi();
  initialize();
  timer_clear(1);
  timer_start(1);
  for (step = 1; step <= niter; step++) {
    if (step % 20 == 0 || step == 1) {
      printf(" Time step %4d\n", step);
    }
    adi();
  }
  {    
#if defined(_OPENMP)
  nthreads = omp_get_num_threads();
#endif   
  } 
  timer_stop(1);
  tmax = timer_read(1);
  verify(niter, &class, &verified);
  if (tmax != 0) {
    mflops = ( 881.174 * pow((double)PROBLEM_SIZE, 3.0)
	       - 4683.91 * pow2((double)PROBLEM_SIZE)
	       + 11484.5 * (double)PROBLEM_SIZE
	       - 19272.4) * (double)niter / (tmax*1000000.0);
  } else {
    mflops = 0.0;
  }
  c_print_results("SP", class, grid_points[0],
		  grid_points[1], grid_points[2], niter, nthreads,
		  tmax, mflops, "          floating point", 
		  verified, NPBVERSION, COMPILETIME, CS1, CS2, CS3, CS4, CS5, 
		  CS6, "(none)");
}
static void add(void) {
  int i, j, k, m;
  for (m = 0; m < 5; m++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = 1, j <= grid_points[1]-2; j++) {
	for (k = 1; k <= grid_points[2]-2; k++) {
	  u[m][i][j][k] = u[m][i][j][k] + rhs[m][i][j][k];
	}
      }
    }
  }
}
static void adi(void) {
  compute_rhs();
  txinvr();
  x_solve();
  y_solve();
  z_solve();
  add();
}
static void error_norm(double rms[5]) {
  int i, j, k, m, d;
  double xi, eta, zeta, u_exact[5], add;
  for (m = 0; m < 5; m++) {
    rms[m] = 0.0;
  }
  for (i = 0; i <= grid_points[0]-1; i++) {
    xi = (double)i * dnxm1;
    for (j = 0; j <= grid_points[1]-1; j++) {
      eta = (double)j * dnym1;
      for (k = 0; k <= grid_points[2]-1; k++) {
	zeta = (double)k * dnzm1;
	exact_solution(xi, eta, zeta, u_exact);
	for (m = 0; m < 5; m++) {
	  add = u[m][i][j][k] - u_exact[m];
	  rms[m] = rms[m] + add*add;
	}
      }
    }
  }
  for (m = 0; m < 5; m++) {
    for (d = 0; d < 3; d++) {
      rms[m] = rms[m] / (double)(grid_points[d]-2);
    }
    rms[m] = sqrt(rms[m]);
  }
}
static void rhs_norm(double rms[5]) {
  int i, j, k, d, m;
  double add;
  for (m = 0; m < 5; m++) {
    rms[m] = 0.0;
  }
  for (i = 0; i <= grid_points[0]-2; i++) {
    for (j = 0; j <= grid_points[1]-2; j++) {
      for (k = 0; k <= grid_points[2]-2; k++) {
	for (m = 0; m < 5; m++) {
	  add = rhs[m][i][j][k];
	  rms[m] = rms[m] + add*add;
	}
      }
    }
  }
  for (m = 0; m < 5; m++) {
    for (d = 0; d < 3; d++) {
      rms[m] = rms[m] / (double)(grid_points[d]-2);
    }
    rms[m] = sqrt(rms[m]);
  }
}
static void exact_rhs(void) {
  double dtemp[5], xi, eta, zeta, dtpp;
  int m, i, j, k, ip1, im1, jp1, jm1, km1, kp1;
  for (m = 0; m < 5; m++) {
    for (i = 0; i <= grid_points[0]-1; i++) {
      for (j = 0; j <= grid_points[1]-1; j++) {
	for (k= 0; k <= grid_points[2]-1; k++) {
	  forcing[m][i][j][k] = 0.0;
	}
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (j = 1; j <= grid_points[1]-2; j++) {
      eta = (double)j * dnym1;
      for (i = 0; i <= grid_points[0]-1; i++) {
	xi = (double)i * dnxm1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][i] = dtemp[m];
	}
	dtpp = 1.0 / dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][i] = dtpp * dtemp[m];
	}
	cuf[i] = buf[1][i] * buf[1][i];
	buf[0][i] = cuf[i] + buf[2][i] * buf[2][i] + buf[3][i] * buf[3][i];
	q[i] = 0.5 * (buf[1][i]*ue[1][i] + buf[2][i]*ue[2][i]
		      + buf[3][i]*ue[3][i]);
      }
      for (i = 1; i <= grid_points[0]-2; i++) {
	im1 = i-1;
	ip1 = i+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  tx2*( ue[1][ip1]-ue[1][im1] )+
	  dx1tx1*(ue[0][ip1]-2.0*ue[0][i]+ue[0][im1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - tx2 * ((ue[1][ip1]*buf[1][ip1]+c2*(ue[4][ip1]-q[ip1]))-
                   (ue[1][im1]*buf[1][im1]+c2*(ue[4][im1]-q[im1])))+
	  xxcon1*(buf[1][ip1]-2.0*buf[1][i]+buf[1][im1])+
	  dx2tx1*( ue[1][ip1]-2.0* ue[1][i]+ue[1][im1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - tx2 * (ue[2][ip1]*buf[1][ip1]-ue[2][im1]*buf[1][im1])+
	  xxcon2*(buf[2][ip1]-2.0*buf[2][i]+buf[2][im1])+
	  dx3tx1*( ue[2][ip1]-2.0*ue[2][i] +ue[2][im1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - tx2*(ue[3][ip1]*buf[1][ip1]-ue[3][im1]*buf[1][im1])+
	  xxcon2*(buf[3][ip1]-2.0*buf[3][i]+buf[3][im1])+
	  dx4tx1*( ue[3][ip1]-2.0* ue[3][i]+ ue[3][im1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - tx2*(buf[1][ip1]*(c1*ue[4][ip1]-c2*q[ip1])-
		 buf[1][im1]*(c1*ue[4][im1]-c2*q[im1]))+
	  0.5*xxcon3*(buf[0][ip1]-2.0*buf[0][i]+
		      buf[0][im1])+
	  xxcon4*(cuf[ip1]-2.0*cuf[i]+cuf[im1])+
	  xxcon5*(buf[4][ip1]-2.0*buf[4][i]+buf[4][im1])+
	  dx5tx1*( ue[4][ip1]-2.0* ue[4][i]+ ue[4][im1]);
      }
      for (m = 0; m < 5; m++) {
	i = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	i = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] +
	   6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue[4][jm1]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (5.0*ue[m][i] - 4.0*ue[m][i+1] +ue[m][i+2]);
	j = 2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (-4.0*ue[m][i-1] + 6.0*ue[m][i] -
 	    4.0*ue[m][i+1] +     ue[m][i+2]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 3; i <= grid_points[0]-4; i++) {
	  forcing[m][i][j][k] = forcing[m][i][j][k] - dssp*
	    (ue[m][i-2] - 4.0*ue[m][i-1] +
	     6.0*ue[m][i] - 4.0*ue[m][i+1] + ue[m][i+2]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 6.0*ue[m][i] - 4.0*ue[m][i+1]);
	i = grid_points[0]-2;
	forcing[m][i][j][k] = forcing[m][i][j][k] - dssp *
	  (ue[m][i-2] - 4.0*ue[m][i-1] + 5.0*ue[m][i]);
      }
    }
  }
  for (k = 1; k <= grid_points[2]-2; k++) {
    zeta = (double)k * dnzm1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      xi = (double)i * dnxm1;
      for (j = 0; j <= grid_points[1]-1; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[m][j] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m < 5; m++) {
	  buf[m][j] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[2][j] * buf[2][j];
	buf[0][j] = cuf[j] + buf[1][j] * buf[1][j] + 
	  buf[3][j] * buf[3][j];
	q[j] = 0.5*(buf[1][j]*ue[1][j] + buf[2][j]*ue[2][j] +
		    buf[3][j]*ue[3][j]);
      }
      for (j = 1; j <= grid_points[1]-2; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[0][i][j][k] = forcing[0][i][j][k] -
	  ty2*( ue[2][jp1]-ue[2][jm1] )+
	  dy1ty1*(ue[0][jp1]-2.0*ue[0][j]+ue[0][jm1]);
	forcing[1][i][j][k] = forcing[1][i][j][k]
	  - ty2*(ue[1][jp1]*buf[2][jp1]-ue[1][jm1]*buf[2][jm1])+
	  yycon2*(buf[1][jp1]-2.0*buf[1][j]+buf[1][jm1])+
	  dy2ty1*( ue[1][jp1]-2.0* ue[1][j]+ ue[1][jm1]);
	forcing[2][i][j][k] = forcing[2][i][j][k]
	  - ty2 * ((ue[2][jp1]*buf[2][jp1]+c2*(ue[4][jp1]-q[jp1]))-
                   (ue[2][jm1]*buf[2][jm1]+c2*(ue[4][jm1]-q[jm1])))+
	  yycon1*(buf[2][jp1]-2.0*buf[2][j]+buf[2][jm1])+
	  dy3ty1*( ue[2][jp1]-2.0*ue[2][j] +ue[2][jm1]);
	forcing[3][i][j][k] = forcing[3][i][j][k]
	  - ty2*(ue[3][jp1]*buf[2][jp1]-ue[3][jm1]*buf[2][jm1])+
	  yycon2*(buf[3][jp1]-2.0*buf[3][j]+buf[3][jm1])+
	  dy4ty1*( ue[3][jp1]-2.0*ue[3][j]+ ue[3][jm1]);
	forcing[4][i][j][k] = forcing[4][i][j][k]
	  - ty2*(buf[2][jp1]*(c1*ue[4][jp1]-c2*q[jp1])-
		 buf[2][jm1]*(c1*ue[4][jm1]-c2*q[jm1]))+
	  0.5*yycon3*(buf[0][jp1]-2.0*buf[0][j]+
		      buf[0][jm1])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[4][jp1]-2.0*buf[4][j]+buf[4][jm1])+
	  dy5ty1*(ue[4][jp1]-2.0*ue[4][j]+ue