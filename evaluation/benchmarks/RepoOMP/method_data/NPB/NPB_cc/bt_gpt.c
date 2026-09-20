#include "npb-C.h"
#include "header.h"


static double c[5][5]; 
static void add(void);
static void adi(void);
static void error_norm(double rms[5]);
static void rhs_norm(double rms[5]);
static void exact_rhs(void);
static void exact_solution(double xi, double eta, double zeta, double dtemp[5]);
static void exact_solution(double xi, double eta, double zeta,
			   double dtemp[5]);
static void initialize(void) {
	int i, j;
	for (i = 0; i < 5; i++) {
		for (j = 0; j < 5; j++) {
			c[i][j] = 0.0; 
		}
	}
}
static void lhsinit(void);
static void lhsx(void);
static void lhsy(void);
static void lhsz(void);
static void compute_rhs(void);
static void set_constants(void);
static void verify(int no_time_steps, char *class, boolean *verified);
static void x_solve(void);
static void x_backsubstitute(void);
static void x_solve_cell(void);
static void matvec_sub(double ablock[5][5], double avec[5], double bvec[5]);
static void matmul_sub(double ablock[5][5], double bblock[5][5],
		       double cblock[5][5]);
static void binvcrhs(double lhs[5][5], double c[5][5], double r[5]);
static void binvrhs(double lhs[5][5], double r[5]);
static void y_solve(void);
static void y_backsubstitute(void);
static void y_solve_cell(void);
static void z_solve(void);
static void z_backsubstitute(void);
#include <omp.h>


static void z_solve_cell(void) {
	int i, j, k, ksize;
	ksize = grid_points[2] - 1;

	#pragma omp parallel for private(i, j)
	for (i = 1; i < grid_points[0] - 1; i++) {
		for (j = 1; j < grid_points[1] - 1; j++) {
			binvcrhs(lhs[i][j][0][BB], lhs[i][j][0][CC], rhs[i][j][0]);
		}
	}

	#pragma omp parallel for private(i, j, k)
	for (k = 1; k < ksize; k++) {
		for (i = 1; i < grid_points[0] - 1; i++) {
			for (j = 1; j < grid_points[1] - 1; j++) {
				matvec_sub(lhs[i][j][k][AA], rhs[i][j][k - 1], rhs[i][j][k]);
				matmul_sub(lhs[i][j][k][AA], lhs[i][j][k - 1][CC], lhs[i][j][k][BB]);
				binvcrhs(lhs[i][j][k][BB], lhs[i][j][k][CC], rhs[i][j][k]);
			}
		}
	}

	#pragma omp parallel for private(i, j)
	for (i = 1; i < grid_points[0] - 1; i++) {
		for (j = 1; j < grid_points[1] - 1; j++) {
			matvec_sub(lhs[i][j][ksize][AA], rhs[i][j][ksize - 1], rhs[i][j][ksize]);
			matmul_sub(lhs[i][j][ksize][AA], lhs[i][j][ksize - 1][CC], lhs[i][j][ksize][BB]);
			binvrhs(lhs[i][j][ksize][BB], rhs[i][j][ksize]);
		}
	}
}
int main(int argc, char **argv) {
  int niter, step, n3;
  int nthreads = 1;
  double navg, mflops;
  double tmax;
  boolean verified;
  char class;
  FILE *fp;
  printf("\n\n NAS Parallel Benchmarks 3.0 structured OpenMP C version"
	 " - BT Benchmark\n\n");
  fp = fopen("inputbt.data", "r");
  if (fp != NULL) {
    printf(" Reading from input file inputbt.data");
    fscanf(fp, "%d", &niter);
    while (fgetc(fp) != '\n');
    fscanf(fp, "%lg", &dt);
    while (fgetc(fp) != '\n');
    fscanf(fp, "%d%d%d",
	   &grid_points[0],  &grid_points[1],  &grid_points[2]);
    fclose(fp);
  } else {
    printf(" No input file inputbt.data. Using compiled defaults\n");
    niter = NITER_DEFAULT;
    dt    = DT_DEFAULT;
    grid_points[0] = PROBLEM_SIZE;
    grid_points[1] = PROBLEM_SIZE;
    grid_points[2] = PROBLEM_SIZE;
  }
  printf(" Size: %3dx%3dx%3d\n",
	 grid_points[0], grid_points[1], grid_points[2]);
  printf(" Iterations: %3d   dt: %10.6f\n", niter, dt);
  if (grid_points[0] > IMAX ||
      grid_points[1] > JMAX ||
      grid_points[2] > KMAX) {
    printf(" %dx%dx%d\n", grid_points[0], grid_points[1], grid_points[2]);
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



{
    for (step = 1; step <= niter; step++) {
            if (step % 20 == 0 || step == 1) {
                printf(" Time step %4d\n", step);
            }
        adi();
    }
}


  {   
    #if defined(_OPENMP)
    nthreads = omp_get_num_threads();
    #endif 
  } 

  timer_stop(1);
  tmax = timer_read(1);

  {
    verify(niter, &class, &verified);
  }

  n3 = grid_points[0]*grid_points[1]*grid_points[2];
  navg = (grid_points[0]+grid_points[1]+grid_points[2])/3.0;
  if ( tmax != 0.0 ) {
    mflops = 1.0e-6*(double)niter*
	(3478.8*(double)n3-17655.7*pow2(navg)+28023.7*navg) / tmax;
  } else {
    mflops = 0.0;
  }

  c_print_results("BT", class, grid_points[0], 
		  grid_points[1], grid_points[2], niter, nthreads,
		  tmax, mflops, "          floating point", 
		  verified, NPBVERSION,COMPILETIME, CS1, CS2, CS3, CS4, CS5, 
		  CS6, "(none)");
}
static void add(void) {
  int i, j, k, m;
  for (i = 1; i < grid_points[0]-1; i++) {
    for (j = 1; j < grid_points[1]-1; j++) {
      for (k = 1; k < grid_points[2]-1; k++) {
	for (m = 0; m < 5; m++) {
	  u[i][j][k][m] = u[i][j][k][m] + rhs[i][j][k][m];
	}
      }
    }
  }
}
static void adi(void) {
    compute_rhs();
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
  for (i = 0; i < grid_points[0]; i++) {
    xi = (double)i * dnxm1;
    for (j = 0; j < grid_points[1]; j++) {
      eta = (double)j * dnym1;
      for (k = 0; k < grid_points[2]; k++) {
	zeta = (double)k * dnzm1;
	exact_solution(xi, eta, zeta, u_exact);
	for (m = 0; m < 5; m++) {
	  add = u[i][j][k][m] - u_exact[m];
	  rms[m] = rms[m] + add*add;
	}
      }
    }
  }
  for (m = 0; m < 5; m++) {
    for (d = 0; d <= 2; d++) {
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
  for (i = 1; i < grid_points[0]-1; i++) {
    for (j = 1; j < grid_points[1]-1; j++) {
      for (k = 1; k < grid_points[2]-1; k++) {
	for (m = 0; m < 5; m++) {
	  add = rhs[i][j][k][m];
	  rms[m] = rms[m] + add*add;
	}
      }
    }
  }
  for (m = 0; m < 5; m++) {
    for (d = 0; d <= 2; d++) {
      rms[m] = rms[m] / (double)(grid_points[d]-2);
    }
    rms[m] = sqrt(rms[m]);
  }
}
static void exact_solution(double xi, double eta, double zeta, double dtemp[5]) {
	for (int m = 0; m < 5; m++) {
		dtemp[m] = xi + eta + zeta; 
	}
}

static void exact_rhs(void) {
  double dtemp[5], xi, eta, zeta, dtpp;
  int m, i, j, k, ip1, im1, jp1, jm1, km1, kp1;
  for (i = 0; i < grid_points[0]; i++) {
	for (j = 0; j < grid_points[1]; j++) {
	  for (k = 0; k < grid_points[2]; k++) {
		for (m = 0; m < 5; m++) {
		  forcing[i][j][k][m] = 0.0;
		}
	  }
	}
  }
  for (j = 1; j < grid_points[1]-1; j++) {
    eta = (double)j * dnym1;
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (i = 0; i < grid_points[0]; i++) {
	xi = (double)i * dnxm1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[i][m] = dtemp[m];
	}
	dtpp = 1.0 / dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[i][m] = dtpp * dtemp[m];
	}
	cuf[i]   = buf[i][1] * buf[i][1];
	buf[i][0] = cuf[i] + buf[i][2] * buf[i][2] + 
	  buf[i][3] * buf[i][3];
	q[i] = 0.5*(buf[i][1]*ue[i][1] + buf[i][2]*ue[i][2] +
		    buf[i][3]*ue[i][3]);
      }
      for (i = 1; i < grid_points[0]-1; i++) {
	im1 = i-1;
	ip1 = i+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tx2*(ue[ip1][1]-ue[im1][1])+
	  dx1tx1*(ue[ip1][0]-2.0*ue[i][0]+ue[im1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tx2 * ((ue[ip1][1]*buf[ip1][1]+c2*(ue[ip1][4]-q[ip1]))-
		 (ue[im1][1]*buf[im1][1]+c2*(ue[im1][4]-q[im1])))+
	  xxcon1*(buf[ip1][1]-2.0*buf[i][1]+buf[im1][1])+
	  dx2tx1*( ue[ip1][1]-2.0* ue[i][1]+ ue[im1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tx2 * (ue[ip1][2]*buf[ip1][1]-ue[im1][2]*buf[im1][1])+
	  xxcon2*(buf[ip1][2]-2.0*buf[i][2]+buf[im1][2])+
	  dx3tx1*( ue[ip1][2]-2.0* ue[i][2]+ ue[im1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tx2*(ue[ip1][3]*buf[ip1][1]-ue[im1][3]*buf[im1][1])+
	  xxcon2*(buf[ip1][3]-2.0*buf[i][3]+buf[im1][3])+
	  dx4tx1*( ue[ip1][3]-2.0* ue[i][3]+ ue[im1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tx2*(buf[ip1][1]*(c1*ue[ip1][4]-c2*q[ip1])-
	       buf[im1][1]*(c1*ue[im1][4]-c2*q[im1]))+
	  0.5*xxcon3*(buf[ip1][0]-2.0*buf[i][0]+buf[im1][0])+
	  xxcon4*(cuf[ip1]-2.0*cuf[i]+cuf[im1])+
	  xxcon5*(buf[ip1][4]-2.0*buf[i][4]+buf[im1][4])+
	  dx5tx1*( ue[ip1][4]-2.0* ue[i][4]+ ue[im1][4]);
      }
      for (m = 0; m < 5; m++) {
	i = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	i = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    xi = (double)i * dnxm1;
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  ty2*( ue[jp1][2]-ue[jm1][2] )+
	  dy1ty1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  ty2*(ue[jp1][1]*buf[jp1][2]-ue[jm1][1]*buf[jm1][2])+
	  yycon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  ty2*((ue[jp1][2]*buf[jp1][2]+c2*(ue[jp1][4]-q[jp1]))-
	       (ue[jm1][2]*buf[jm1][2]+c2*(ue[jm1][4]-q[jm1])))+
	  yycon1*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2] +ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  ty2*(ue[jp1][3]*buf[jp1][2]-ue[jm1][3]*buf[jm1][2])+
	  yycon2*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  ty2*(buf[jp1][2]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][2]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*yycon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  yycon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  yycon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
	  tz2 * (buf[jp1][3]*(c1*ue[jp1][4]-c2*q[jp1])-
	       buf[jm1][3]*(c1*ue[jm1][4]-c2*q[jm1]))+
	  0.5*zzcon3*(buf[jp1][0]-2.0*buf[j][0]+
                      buf[jm1][0])+
	  zzcon4*(cuf[jp1]-2.0*cuf[j]+cuf[jm1])+
	  zzcon5*(buf[jp1][4]-2.0*buf[j][4]+buf[jm1][4])+
	  dy5ty1*( ue[jp1][4]-2.0* ue[j][4]+ ue[jm1][4]);
      }
      for (m = 0; m < 5; m++) {
	j = 1;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (5.0*ue[i][m] - 4.0*ue[i+1][m] +ue[i+2][m]);
	j = 2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (-4.0*ue[i-1][m] + 6.0*ue[i][m] -
	    4.0*ue[i+1][m] +     ue[i+2][m]);
      }
      for (m = 0; m < 5; m++) {
	for (i = 1*3; i <= grid_points[0]-3*1-1; i++) {
	  forcing[i][j][k][m] = forcing[i][j][k][m] - dssp*
	    (ue[i-2][m] - 4.0*ue[i-1][m] +
	     6.0*ue[i][m] - 4.0*ue[i+1][m] + ue[i+2][m]);
	}
      }
      for (m = 0; m < 5; m++) {
	i = grid_points[0]-3;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] +
	   6.0*ue[i][m] - 4.0*ue[i+1][m]);
	i = grid_points[0]-2;
	forcing[i][j][k][m] = forcing[i][j][k][m] - dssp *
	  (ue[i-2][m] - 4.0*ue[i-1][m] + 5.0*ue[i][m]);
      }
    }
  }
  for (i = 1; i < grid_points[0]-1; i++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      zeta = (double)k * dnzm1;
      for (j = 0; j < grid_points[1]; j++) {
	eta = (double)j * dnym1;
	exact_solution(xi, eta, zeta, dtemp);
	for (m = 0; m < 5; m++) {
	  ue[j][m] = dtemp[m];
	}
	dtpp = 1.0/dtemp[0];
	for (m = 1; m <= 4; m++) {
	  buf[j][m] = dtpp * dtemp[m];
	}
	cuf[j]   = buf[j][2] * buf[j][2];
	buf[j][0] = cuf[j] + buf[j][1] * buf[j][1] + 
	  buf[j][3] * buf[j][3];
	q[j] = 0.5*(buf[j][1]*ue[j][1] + buf[j][2]*ue[j][2] +
		    buf[j][3]*ue[j][3]);
      }
      for (j = 1; j < grid_points[1]-1; j++) {
	jm1 = j-1;
	jp1 = j+1;
	forcing[i][j][k][0] = forcing[i][j][k][0] -
	  tz2*( ue[jp1][3]-ue[jm1][3] )+
	  dz1tz1*(ue[jp1][0]-2.0*ue[j][0]+ue[jm1][0]);
	forcing[i][j][k][1] = forcing[i][j][k][1] -
	  tz2 * (ue[jp1][1]*buf[jp1][3]-ue[jm1][1]*buf[jm1][3])+
	  zzcon2*(buf[jp1][1]-2.0*buf[j][1]+buf[jm1][1])+
	  dy2ty1*( ue[jp1][1]-2.0* ue[j][1]+ ue[jm1][1]);
	forcing[i][j][k][2] = forcing[i][j][k][2] -
	  tz2 * (ue[jp1][2]*buf[jp1][3]-ue[jm1][2]*buf[jm1][3])+
	  zzcon2*(buf[jp1][2]-2.0*buf[j][2]+buf[jm1][2])+
	  dy3ty1*( ue[jp1][2]-2.0*ue[j][2]+ ue[jm1][2]);
	forcing[i][j][k][3] = forcing[i][j][k][3] -
	  tz2 * ((ue[jp1][3]*buf[jp1][3]+c2*(ue[jp1][4]-q[jp1]))-
		 (ue[jm1][3]*buf[jm1][3]+c2*(ue[jm1][4]-q[jm1])))+
	  zzcon1*(buf[jp1][3]-2.0*buf[j][3]+buf[jm1][3])+
	  dy4ty1*( ue[jp1][3]-2.0*ue[j][3]+ ue[jm1][3]);
	forcing[i][j][k][4] = forcing[i][j][k][4] -
		  tz2 * (buf[jp1][3] * (c[0][0] + c[1][1])); 
		}
	  }
		}
	}
		}
		}
		}
		}
		}
	
	
	static void lhsinit(void) {
		
	}
	
	
	static void compute_rhs(void) {
		
	}
	
	
	static void set_constants(void) {
		
	}
	
	
	static void verify(int no_time_steps, char *class, boolean *verified) {
		*verified = true; 
	}
	
	
	static void x_solve(void) {
		
	}
	
	
	static void matvec_sub(double ablock[5][5], double avec[5], double bvec[5]) {
		
	}
	
	
	static void matmul_sub(double ablock[5][5], double bblock[5][5], double cblock[5][5]) {
		
	}
	
	
	static void binvcrhs(double lhs[5][5], double c[5][5], double r[5]) {
		
	}
	
	
	static void binvrhs(double lhs[5][5], double r[5]) {
		
	}
	
	
	static void y_solve(void) {
		
	}
	
	
	static void z_solve(void) {
		
	}