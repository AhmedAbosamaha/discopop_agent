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
static void z_solve_cell(void);
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
#pragma omp parallel for private(j, k, m)
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
static void exact_rhs(void) {
{
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
	  0.5*yycon3*(buf[jp1][0]-2.0*buf[j][0]+buf[jm1][0])+
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
	  0.5*yycon3*(buf[jp1][0]-2.0*buf[j][0]+buf[jm1][0])+
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
    for (j = 1; j < grid_points[1]-1; j++) {
      for (k = 1; k < grid_points[2]-1; k++) {
	for (m = 0; m < 5; m++) {
	  forcing[i][j][k][m] = -1.0 * forcing[i][j][k][m];
	}
      }
    }
  }
}
}
static void exact_solution(double xi, double eta, double zeta,
			   double dtemp[5]) {
  int m;
  for (m = 0; m < 5; m++) {
    dtemp[m] =  ce[m][0] +
      xi*(ce[m][1] + xi*(ce[m][4] + xi*(ce[m][7]
					+ xi*ce[m][10]))) +
      eta*(ce[m][2] + eta*(ce[m][5] + eta*(ce[m][8]
					   + eta*ce[m][11])))+
      zeta*(ce[m][3] + zeta*(ce[m][6] + zeta*(ce[m][9] + 
					      zeta*ce[m][12])));
  }
}
static void initialize(void) {
{
  int i, j, k, m, ix, iy, iz;
  double xi, eta, zeta, Pface[2][3][5], Pxi, Peta, Pzeta, temp[5];
  for (i = 0; i < IMAX; i++) {
    for (j = 0; j < IMAX; j++) {
      for (k = 0; k < IMAX; k++) {
	for (m = 0; m < 5; m++) {
	  u[i][j][k][m] = 1.0;
	}
      }
    }
  }
  for (i = 0; i < grid_points[0]; i++) {
    xi = (double)i * dnxm1;
    for (j = 0; j < grid_points[1]; j++) {
      eta = (double)j * dnym1;
      for (k = 0; k < grid_points[2]; k++) {
	zeta = (double)k * dnzm1;
	for (ix = 0; ix < 2; ix++) {
	  exact_solution((double)ix, eta, zeta, 
                         &(Pface[ix][0][0]));
	}
	for (iy = 0; iy < 2; iy++) {
	  exact_solution(xi, (double)iy , zeta, 
                         &Pface[iy][1][0]);
	}
	for (iz = 0; iz < 2; iz++) {
	  exact_solution(xi, eta, (double)iz,   
                         &Pface[iz][2][0]);
	}
	for (m = 0; m < 5; m++) {
	  Pxi   = xi   * Pface[1][0][m] + 
	    (1.0-xi)   * Pface[0][0][m];
	  Peta  = eta  * Pface[1][1][m] + 
	    (1.0-eta)  * Pface[0][1][m];
	  Pzeta = zeta * Pface[1][2][m] + 
	    (1.0-zeta) * Pface[0][2][m];
	  u[i][j][k][m] = Pxi + Peta + Pzeta - 
	    Pxi*Peta - Pxi*Pzeta - Peta*Pzeta + 
	    Pxi*Peta*Pzeta;
	}
      }
    }
  }
  i = 0;
  xi = 0.0;
  for (j = 0; j < grid_points[1]; j++) {
    eta = (double)j * dnym1;
    for (k = 0; k < grid_points[2]; k++) {
      zeta = (double)k * dnzm1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) {
	u[i][j][k][m] = temp[m];
      }
    }
  }
  i = grid_points[0]-1;
  xi = 1.0;
  for (j = 0; j < grid_points[1]; j++) {
    eta = (double)j * dnym1;
    for (k = 0; k < grid_points[2]; k++) {
      zeta = (double)k * dnzm1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) {
	u[i][j][k][m] = temp[m];
      }
    }
  }
  j = 0;
  eta = 0.0;
  for (i = 0; i < grid_points[0]; i++) {
    xi = (double)i * dnxm1;
    for (k = 0; k < grid_points[2]; k++) {
      zeta = (double)k * dnzm1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) {
	u[i][j][k][m] = temp[m];
      }
    }
  }
  j = grid_points[1]-1;
  eta = 1.0;
  for (i = 0; i < grid_points[0]; i++) {
    xi = (double)i * dnxm1;
    for (k = 0; k < grid_points[2]; k++) {
      zeta = (double)k * dnzm1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) {
	u[i][j][k][m] = temp[m];
      }
    }
  }
  k = 0;
  zeta = 0.0;
  for (i = 0; i < grid_points[0]; i++) {
    xi = (double)i *dnxm1;
    for (j = 0; j < grid_points[1]; j++) {
      eta = (double)j * dnym1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) {
	u[i][j][k][m] = temp[m];
      }
    }
  }
  k = grid_points[2]-1;
  zeta = 1.0;
  for (i = 0; i < grid_points[0]; i++) {
    xi = (double)i * dnxm1;
    for (j = 0; j < grid_points[1]; j++) {
      eta = (double)j * dnym1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) {
	u[i][j][k][m] = temp[m];
      }
    }
  }
}
}
static void lhsinit(void) {
{
  int i, j, k, m, n;
  for (i = 0; i < grid_points[0]; i++) {
    for (j = 0; j < grid_points[1]; j++) {
      for (k = 0; k < grid_points[2]; k++) {
	for (m = 0; m < 5; m++) {
	  for (n = 0; n < 5; n++) {
	    lhs[i][j][k][0][m][n] = 0.0;
	    lhs[i][j][k][1][m][n] = 0.0;
	    lhs[i][j][k][2][m][n] = 0.0;
	  }
	}
      }
    }
  }
  for (i = 0; i < grid_points[0]; i++) {
    for (j = 0; j < grid_points[1]; j++) {
      for (k = 0; k < grid_points[2]; k++) {
	for (m = 0; m < 5; m++) {
	  lhs[i][j][k][1][m][m] = 1.0;
	}
      }
    }
  }
}
}
static void lhsx(void) {
  int i, j, k;
#pragma omp parallel for private(k, i, tmp1, tmp2, tmp3)
  for (j = 1; j < grid_points[1]-1; j++) {
    for (k = 1; k < grid_points[2]-1; k++) {
      for (i = 0; i < grid_points[0]; i++) {
	tmp1 = 1.0 / u[i][j][k][0];
	tmp2 = tmp1 * tmp1;
	tmp3 = tmp1 * tmp2;
	fjac[ i][ j][ k][0][0] = 0.0;
	fjac[ i][ j][ k][0][1] = 1.0;
	fjac[ i][ j][ k][0][2] = 0.0;
	fjac[ i][ j][ k][0][3] = 0.0;
	fjac[ i][ j][ k][0][4] = 0.0;
	fjac[ i][ j][ k][1][0] = -(u[i][j][k][1] * tmp2 * 
				    u[i][j][k][1])
	  + c2 * 0.50 * (u[i][j][k][1] * u[i][j][k][1]
		       + u[i][j][k][2] * u[i][j][k][2]
		       + u[i][j][k][3] * u[i][j][k][3] ) * tmp2;
	fjac[i][j][k][1][1] = ( 2.0 - c2 )
	  * ( u[i][j][k][1] / u[i][j][k][0] );
	fjac[i][j][k][1][2] = - c2 * ( u[i][j][k][2] * tmp1 );
	fjac[i][j][k][1][3] = - c2 * ( u[i][j][k][3] * tmp1 );
	fjac[i][j][k][1][4] = c2;
	fjac[i][j][k][2][0] = - ( u[i][j][k][1]*u[i][j][k][2] ) * tmp2;
	fjac[i][j][k][2][1] = u[i][j][k][2] * tmp1;
	fjac[i][j][k][2][2] = u[i][j][k][1] * tmp1;
	fjac[i][j][k][2][3] = 0.0;
	fjac[i][j][k][2][4] = 0.0;
	fjac[i][j][k][3][0] = - ( u[i][j][k][1]*u[i][j][k][3] ) * tmp2;
	fjac[i][j][k][3][1] = u[i][j][k][3] * tmp1;
	fjac[i][j][k][3][2] = 0.0;
	fjac[i][j][k][3][3] = u[i][j][k][1] * tmp1;
	fjac[i][j][k][3][4] = 0.0;
	fjac[i][j][k][4][0] = ( c2 * ( u[i][j][k][1] * u[i][j][k][1]
				     + u[i][j][k][2] * u[i][j][k][2]
				     + u[i][j][k][3] * u[i][j][k][3] ) * tmp2
				- c1 * ( u[i][j][k][4] * tmp1 ) )
	  * ( u[i][j][k][1] * tmp1 );
	fjac[i][j][k][4][1] = c1 *  u[i][j][k][4] * tmp1 
	  - 0.50 * c2
	  * (  3.0*u[i][j][k][1]*u[i][j][k][1]
	       + u[i][j][k][2]*u[i][j][k][2]
	       + u[i][j][k][3]*u[i][j][k][3] ) * tmp2;
	fjac[i][j][k][4][2] = - c2 * ( u[i][j][k][2]*u[i][j][k][1] )
	  * tmp2;
	fjac[i][j][k][4][3] = - c2 * ( u[i][j][k][3]*u[i][j][k][1] )
	  * tmp2;
	fjac[i][j][k][4][4] = c1 * ( u[i][j][k][1] * tmp1 );
	njac[i][j][k][0][0] = 0.0;
	njac[i][j][k][0][1] = 0.0;
	njac[i][j][k][0][2] = 0.0;
	njac[i][j][k][0][3] = 0.0;
	njac[i][j][k][0][4] = 0.0;
	njac[i][j][k][1][0] = - con43 * c3c4 * tmp2 * u[i][j][k][1];
	njac[i][j][k][1][1] =   con43 * c3c4 * tmp1;
	njac[i][j][k][1][2] =   0.0;
	njac[i][j][k][1][3] =   0.0;
	njac[i][j][k][1][4] =   0.0;
	njac[i][j][k][2][0] = - c3c4 * tmp2 * u[i][j][k][2];
	njac[i][j][k][2][1] =   0.0;
	njac[i][j][k][2][2] =   c3c4 * tmp1;
	njac[i][j][k][2][3] =   0.0;
	njac[i][j][k][2][4] =   0.0;
	njac[i][j][k][3][0] = - c3c4 * tmp2 * u[i][j][k][3];
	njac[i][j][k][3][1] =   0.0;
	njac[i][j][k][3][2] =   0.0;
	njac[i][j][k][3][3] =   c3c4 * tmp1;
	njac[i][j][k][3][4] =   0.0;
	njac[i][j][k][4][0] = - ( con43 * c3c4
	  - c1345 ) * tmp3 * (pow2(u[i][j][k][1]))
	  - ( c3c4 - c1345 ) * tmp3 * (pow2(u[i][j][k][2]))
	  - ( c3c4 - c1345 ) * tmp3 * (pow2(u[i][j][k][3]))
	  - c1345 * tmp2 * u[i][j][k][4];
	njac[i][j][k][4][1] = ( con43 * c3c4
				- c1345 ) * tmp2 * u[i][j][k][1];
	njac[i][j][k][4][2] = ( c3c4 - c1345 ) * tmp2 * u[i][j][k][2];
	njac[i][j][k][4][3] = ( c3c4 - c1345 ) * tmp2 * u[i][j][k][3];
	njac[i][j][k][4][4] = ( c1345 ) * tmp1;
      }
      for (i = 1; i < grid_points[0]-1; i++) {
	tmp1 = dt * tx1;
	tmp2 = dt * tx2;
	lhs[i][j][k][AA][0][0] = - tmp2 * fjac[i-1][j][k][0][0]
	  - tmp1 * njac[i-1][j][k][0][0]
	  - tmp1 * dx1;
	lhs[i][j][k][AA][0][1] = - tmp2 * fjac[i-1][j][k][0][1]
	  - tmp1 * njac[i-1][j][k][0][1];
	lhs[i][j][k][AA][0][2] = - tmp2 * fjac[i-1][j][k][0][2]
	  - tmp1 * njac[i-1][j][k][0][2];
	lhs[i][j][k][AA][0][3] = - tmp2 * fjac[i-1][j][k][0][3]
	  - tmp1 * njac[i-1][j][k][0][3];
	lhs[i][j][k][AA][0][4] = - tmp2 * fjac[i-1][j][k][0][4]
	  - tmp1 * njac[i-1][j][k][0][4];
	lhs[i][j][k][AA][1][0] = - tmp2 * fjac[i-1][j][k][1][0]
	  - tmp1 * njac[i-1][j][k][1][0];
	lhs[i][j][k][AA][1][1] = - tmp2 * fjac[i-1][j][k][1][1]
	  - tmp1 * njac[i-1][j][k][1][1]
	  - tmp1 * dx2;
	lhs[i][j][k][AA][1][2] = - tmp2 * fjac[i-1][j][k][1][2]
	  - tmp1 * njac[i-1][j][k][1][2];
	lhs[i][j][k][AA][1][3] = - tmp2 * fjac[i-1][j][k][1][3]
	  - tmp1 * njac[i-1][j][k][1][3];
	lhs[i][j][k][AA][1][4] = - tmp2 * fjac[i-1][j][k][1][4]
	  - tmp1 * njac[i-1][j][k][1][4];
	lhs[i][j][k][AA][2][0] = - tmp2 * fjac[i-1][j][k][2][0]
	  - tmp1 * njac[i-1][j][k][2][0];
	lhs[i][j][k][AA][2][1] = - tmp2 * fjac[i-1][j][k][2][1]
	  - tmp1 * njac[i-1][j][k][2][1];
	lhs[i][j][k][AA][2][2] = - tmp2 * fjac[i-1][j][k][2][2]
	  - tmp1 * njac[i-1][j][k][2][2]
	  - tmp1 * dx3;
	lhs[i][j][k][AA][2][3] = - tmp2 * fjac[i-1][j][k][2][3]
	  - tmp1 * njac[i-1][j][k][2][3];
	lhs[i][j][k][AA][2][4] = - tmp2 * fjac[i-1][j][k][2][4]
	  - tmp1 * njac[i-1][j][k][2][4];
	lhs[i][j][k][AA][3][0] = - tmp2 * fjac[i-1][j][k][3][0]
	  - tmp1 * njac[i-1][j][k][3][0];
	lhs[i][j][k][AA][3][1] = - tmp2 * fjac[i-1][j][k][3][1]
	  - tmp1 * njac[i-1][j][k][3][1];
	lhs[i][j][k][AA][3][2] = - tmp2 * fjac[i-1][j][k][3][2]
	  - tmp1 * njac[i-1][j][k][3][2];
	lhs[i][j][k][AA][3][3] = - tmp2 * fjac[i-1][j][k][3][3]
	  - tmp1 * njac[i-1][j][k][3][3]
	  - tmp1 * dx4;
	lhs[i][j][k][AA][3][4] = - tmp2 * fjac[i-1][j][k][3][4]
	  - tmp1 * njac[i-1][j][k][3][4];
	lhs[i][j][k][AA][4][0] = - tmp2 * fjac[i-1][j][k][4][0]
	  - tmp1 * njac[i-1][j][k][4][0];
	lhs[i][j][k][AA][4][1] = - tmp2 * fjac[i-1][j][k][4][1]
	  - tmp1 * njac[i-1][j][k][4][1];
	lhs[i][j][k][AA][4][2] = - tmp2 * fjac[i-1][j][k][4][2]
	  - tmp1 * njac[i-1][j][k][4][2];
	lhs[i][j][k][AA][4][3] = - tmp2 * fjac[i-1][j][k][4][3]
	  - tmp1 * njac[i-1][j][k][4][3];
	lhs[i][j][k][AA][4][4] = - tmp2 * fjac[i-1][j][k][4][4]
	  - tmp1 * njac[i-1][j][k][4][4]
	  - tmp1 * dx5;
	lhs[i][j][k][BB][0][0] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][0][0]
	  + tmp1 * 2.0 * dx1;
	lhs[i][j][k][BB][0][1] = tmp1 * 2.0 * njac[i][j][k][0][1];
	lhs[i][j][k][BB][0][2] = tmp1 * 2.0 * njac[i][j][k][0][2];
	lhs[i][j][k][BB][0][3] = tmp1 * 2.0 * njac[i][j][k][0][3];
	lhs[i][j][k][BB][0][4] = tmp1 * 2.0 * njac[i][j][k][0][4];
	lhs[i][j][k][BB][1][0] = tmp1 * 2.0 * njac[i][j][k][1][0];
	lhs[i][j][k][BB][1][1] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][1][1]
	  + tmp1 * 2.0 * dx2;
	lhs[i][j][k][BB][1][2] = tmp1 * 2.0 * njac[i][j][k][1][2];
	lhs[i][j][k][BB][1][3] = tmp1 * 2.0 * njac[i][j][k][1][3];
	lhs[i][j][k][BB][1][4] = tmp1 * 2.0 * njac[i][j][k][1][4];
	lhs[i][j][k][BB][2][0] = tmp1 * 2.0 * njac[i][j][k][2][0];
	lhs[i][j][k][BB][2][1] = tmp1 * 2.0 * njac[i][j][k][2][1];
	lhs[i][j][k][BB][2][2] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][2][2]
	  + tmp1 * 2.0 * dx3;
	lhs[i][j][k][BB][2][3] = tmp1 * 2.0 * njac[i][j][k][2][3];
	lhs[i][j][k][BB][2][4] = tmp1 * 2.0 * njac[i][j][k][2][4];
	lhs[i][j][k][BB][3][0] = tmp1 * 2.0 * njac[i][j][k][3][0];
	lhs[i][j][k][BB][3][1] = tmp1 * 2.0 * njac[i][j][k][3][1];
	lhs[i][j][k][BB][3][2] = tmp1 * 2.0 * njac[i][j][k][3][2];
	lhs[i][j][k][BB][3][3] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][3][3]
	  + tmp1 * 2.0 * dx4;
	lhs[i][j][k][BB][3][4] = tmp1 * 2.0 * njac[i][j][k][3][4];
	lhs[i][j][k][BB][4][0] = tmp1 * 2.0 * njac[i][j][k][4][0];
	lhs[i][j][k][BB][4][1] = tmp1 * 2.0 * njac[i][j][k][4][1];
	lhs[i][j][k][BB][4][2] = tmp1 * 2.0 * njac[i][j][k][4][2];
	lhs[i][j][k][BB][4][3] = tmp1 * 2.0 * njac[i][j][k][4][3];
	lhs[i][j][k][BB][4][4] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][4][4]
	  + tmp1 * 2.0 * dx5;
	lhs[i][j][k][CC][0][0] =  tmp2 * fjac[i+1][j][k][0][0]
	  - tmp1 * njac[i+1][j][k][0][0]
	  - tmp1 * dx1;
	lhs[i][j][k][CC][0][1] =  tmp2 * fjac[i+1][j][k][0][1]
	  - tmp1 * njac[i+1][j][k][0][1];
	lhs[i][j][k][CC][0][2] =  tmp2 * fjac[i+1][j][k][0][2]
	  - tmp1 * njac[i+1][j][k][0][2];
	lhs[i][j][k][CC][0][3] =  tmp2 * fjac[i+1][j][k][0][3]
	  - tmp1 * njac[i+1][j][k][0][3];
	lhs[i][j][k][CC][0][4] =  tmp2 * fjac[i+1][j][k][0][4]
	  - tmp1 * njac[i+1][j][k][0][4];
	lhs[i][j][k][CC][1][0] =  tmp2 * fjac[i+1][j][k][1][0]
	  - tmp1 * njac[i+1][j][k][1][0];
	lhs[i][j][k][CC][1][1] =  tmp2 * fjac[i+1][j][k][1][1]
	  - tmp1 * njac[i+1][j][k][1][1]
	  - tmp1 * dx2;
	lhs[i][j][k][CC][1][2] =  tmp2 * fjac[i+1][j][k][1][2]
	  - tmp1 * njac[i+1][j][k][1][2];
	lhs[i][j][k][CC][1][3] =  tmp2 * fjac[i+1][j][k][1][3]
	  - tmp1 * njac[i+1][j][k][1][3];
	lhs[i][j][k][CC][1][4] =  tmp2 * fjac[i+1][j][k][1][4]
	  - tmp1 * njac[i+1][j][k][1][4];
	lhs[i][j][k][CC][2][0] =  tmp2 * fjac[i+1][j][k][2][0]
	  - tmp1 * njac[i+1][j][k][2][0];
	lhs[i][j][k][CC][2][1] =  tmp2 * fjac[i+1][j][k][2][1]
	  - tmp1 * njac[i+1][j][k][2][1];
	lhs[i][j][k][CC][2][2] =  tmp2 * fjac[i+1][j][k][2][2]
	  - tmp1 * njac[i+1][j][k][2][2]
	  - tmp1 * dx3;
	lhs[i][j][k][CC][2][3] =  tmp2 * fjac[i+1][j][k][2][3]
	  - tmp1 * njac[i+1][j][k][2][3];
	lhs[i][j][k][CC][2][4] =  tmp2 * fjac[i+1][j][k][2][4]
	  - tmp1 * njac[i+1][j][k][2][4];
	lhs[i][j][k][CC][3][0] =  tmp2 * fjac[i+1][j][k][3][0]
	  - tmp1 * njac[i+1][j][k][3][0];
	lhs[i][j][k][CC][3][1] =  tmp2 * fjac[i+1][j][k][3][1]
	  - tmp1 * njac[i+1][j][k][3][1];
	lhs[i][j][k][CC][3][2] =  tmp2 * fjac[i+1][j][k][3][2]
	  - tmp1 * njac[i+1][j][k][3][2];
	lhs[i][j][k][CC][3][3] =  tmp2 * fjac[i+1][j][k][3][3]
	  - tmp1 * njac[i+1][j][k][3][3]
	  - tmp1 * dx4;
	lhs[i][j][k][CC][3][4] =  tmp2 * fjac[i+1][j][k][3][4]
	  - tmp1 * njac[i+1][j][k][3][4];
	lhs[i][j][k][CC][4][0] =  tmp2 * fjac[i+1][j][k][4][0]
	  - tmp1 * njac[i+1][j][k][4][0];
	lhs[i][j][k][CC][4][1] =  tmp2 * fjac[i+1][j][k][4][1]
	  - tmp1 * njac[i+1][j][k][4][1];
	lhs[i][j][k][CC][4][2] =  tmp2 * fjac[i+1][j][k][4][2]
	  - tmp1 * njac[i+1][j][k][4][2];
	lhs[i][j][k][CC][4][3] =  tmp2 * fjac[i+1][j][k][4][3]
	  - tmp1 * njac[i+1][j][k][4][3];
	lhs[i][j][k][CC][4][4] =  tmp2 * fjac[i+1][j][k][4][4]
	  - tmp1 * njac[i+1][j][k][4][4]
	  - tmp1 * dx5;
      }
    }
  }
}
static void lhsy(void) {
  int i, j, k;
#pragma omp parallel for private(j, k, tmp1, tmp2, tmp3)
  for (i = 1; i < grid_points[0]-1; i++) {
    for (j = 0; j < grid_points[1]; j++) {
      for (k = 1; k < grid_points[2]-1; k++) {
	tmp1 = 1.0 / u[i][j][k][0];
	tmp2 = tmp1 * tmp1;
	tmp3 = tmp1 * tmp2;
	fjac[ i][ j][ k][0][0] = 0.0;
	fjac[ i][ j][ k][0][1] = 0.0;
	fjac[ i][ j][ k][0][2] = 1.0;
	fjac[ i][ j][ k][0][3] = 0.0;
	fjac[ i][ j][ k][0][4] = 0.0;
	fjac[i][j][k][1][0] = - ( u[i][j][k][1]*u[i][j][k][2] )
	  * tmp2;
	fjac[i][j][k][1][1] = u[i][j][k][2] * tmp1;
	fjac[i][j][k][1][2] = u[i][j][k][1] * tmp1;
	fjac[i][j][k][1][3] = 0.0;
	fjac[i][j][k][1][4] = 0.0;
	fjac[i][j][k][2][0] = - ( u[i][j][k][2]*u[i][j][k][2]*tmp2)
	  + 0.50 * c2 * ( (  u[i][j][k][1] * u[i][j][k][1]
			     + u[i][j][k][2] * u[i][j][k][2]
			     + u[i][j][k][3] * u[i][j][k][3] )
			  * tmp2 );
	fjac[i][j][k][2][1] = - c2 *  u[i][j][k][1] * tmp1;
	fjac[i][j][k][2][2] = ( 2.0 - c2 )
	  *  u[i][j][k][2] * tmp1;
	fjac[i][j][k][2][3] = - c2 * u[i][j][k][3] * tmp1;
	fjac[i][j][k][2][4] = c2;
	fjac[i][j][k][3][0] = - ( u[i][j][k][2]*u[i][j][k][3] )
	  * tmp2;
	fjac[i][j][k][3][1] = 0.0;
	fjac[i][j][k][3][2] = u[i][j][k][3] * tmp1;
	fjac[i][j][k][3][3] = u[i][j][k][2] * tmp1;
	fjac[i][j][k][3][4] = 0.0;
	fjac[i][j][k][4][0] = ( c2 * (  u[i][j][k][1] * u[i][j][k][1]
				     + u[i][j][k][2] * u[i][j][k][2]
				     + u[i][j][k][3] * u[i][j][k][3] ) * tmp2
				- c1 * u[i][j][k][4] * tmp1 ) 
	  * u[i][j][k][2] * tmp1;
	fjac[i][j][k][4][1] = - c2 * u[i][j][k][1]*u[i][j][k][2] 
	  * tmp2;
	fjac[i][j][k][4][2] = c1 * u[i][j][k][4] * tmp1 
	  - 0.50 * c2 
	  * ( (  u[i][j][k][1]*u[i][j][k][1]
		 + 3.0 * u[i][j][k][2]*u[i][j][k][2]
		 + u[i][j][k][3]*u[i][j][k][3] )
	      * tmp2 );
	fjac[i][j][k][4][3] = - c2 * ( u[i][j][k][2]*u[i][j][k][3] )
	  * tmp2;
	fjac[i][j][k][4][4] = c1 * u[i][j][k][3] * tmp1; 
	njac[i][j][k][0][0] = 0.0;
	njac[i][j][k][0][1] = 0.0;
	njac[i][j][k][0][2] = 0.0;
	njac[i][j][k][0][3] = 0.0;
	njac[i][j][k][0][4] = 0.0;
	njac[i][j][k][1][0] = - c3c4 * tmp2 * u[i][j][k][1];
	njac[i][j][k][1][1] =   c3c4 * tmp1;
	njac[i][j][k][1][2] =   0.0;
	njac[i][j][k][1][3] =   0.0;
	njac[i][j][k][1][4] =   0.0;
	njac[i][j][k][2][0] = - con43 * c3c4 * tmp2 * u[i][j][k][2];
	njac[i][j][k][2][1] =   0.0;
	njac[i][j][k][2][2] =   con43 * c3c4 * tmp1;
	njac[i][j][k][2][3] =   0.0;
	njac[i][j][k][2][4] =   0.0;
	njac[i][j][k][3][0] = - c3c4 * tmp2 * u[i][j][k][3];
	njac[i][j][k][3][1] =   0.0;
	njac[i][j][k][3][2] =   0.0;
	njac[i][j][k][3][3] =   c3c4 * tmp1;
	njac[i][j][k][3][4] =   0.0;
	njac[i][j][k][4][0] = - ( con43 * c3c4
	  - c1345 ) * tmp3 * (pow2(u[i][j][k][1]))
	  - ( c3c4 - c1345 ) * tmp3 * (pow2(u[i][j][k][2]))
	  - ( c3c4 - c1345 ) * tmp3 * (pow2(u[i][j][k][3]))
	  - c1345 * tmp2 * u[i][j][k][4];
	njac[i][j][k][4][1] = ( con43 * c3c4
				- c1345 ) * tmp2 * u[i][j][k][1];
	njac[i][j][k][4][2] = ( c3c4 - c1345 ) * tmp2 * u[i][j][k][2];
	njac[i][j][k][4][3] = ( c3c4 - c1345 ) * tmp2 * u[i][j][k][3];
	njac[i][j][k][4][4] = ( c1345 ) * tmp1;
      }
      for (i = 1; i < grid_points[0]-1; i++) {
	tmp1 = dt * tx1;
	tmp2 = dt * tx2;
	lhs[i][j][k][AA][0][0] = - tmp2 * fjac[i-1][j][k][0][0]
	  - tmp1 * njac[i-1][j][k][0][0]
	  - tmp1 * dx1;
	lhs[i][j][k][AA][0][1] = - tmp2 * fjac[i-1][j][k][0][1]
	  - tmp1 * njac[i-1][j][k][0][1];
	lhs[i][j][k][AA][0][2] = - tmp2 * fjac[i-1][j][k][0][2]
	  - tmp1 * njac[i-1][j][k][0][2];
	lhs[i][j][k][AA][0][3] = - tmp2 * fjac[i-1][j][k][0][3]
	  - tmp1 * njac[i-1][j][k][0][3];
	lhs[i][j][k][AA][0][4] = - tmp2 * fjac[i-1][j][k][0][4]
	  - tmp1 * njac[i-1][j][k][0][4];
	lhs[i][j][k][AA][1][0] = - tmp2 * fjac[i-1][j][k][1][0]
	  - tmp1 * njac[i-1][j][k][1][0];
	lhs[i][j][k][AA][1][1] = - tmp2 * fjac[i-1][j][k][1][1]
	  - tmp1 * njac[i-1][j][k][1][1]
	  - tmp1 * dx2;
	lhs[i][j][k][AA][1][2] = - tmp2 * fjac[i-1][j][k][1][2]
	  - tmp1 * njac[i-1][j][k][1][2];
	lhs[i][j][k][AA][1][3] = - tmp2 * fjac[i-1][j][k][1][3]
	  - tmp1 * njac[i-1][j][k][1][3];
	lhs[i][j][k][AA][1][4] = - tmp2 * fjac[i-1][j][k][1][4]
	  - tmp1 * njac[i-1][j][k][1][4];
	lhs[i][j][k][AA][2][0] = - tmp2 * fjac[i-1][j][k][2][0]
	  - tmp1 * njac[i-1][j][k][2][0];
	lhs[i][j][k][AA][2][1] = - tmp2 * fjac[i-1][j][k][2][1]
	  - tmp1 * njac[i-1][j][k][2][1];
	lhs[i][j][k][AA][2][2] = - tmp2 * fjac[i-1][j][k][2][2]
	  - tmp1 * njac[i-1][j][k][2][2]
	  - tmp1 * dx3;
	lhs[i][j][k][AA][2][3] = - tmp2 * fjac[i-1][j][k][2][3]
	  - tmp1 * njac[i-1][j][k][2][3];
	lhs[i][j][k][AA][2][4] = - tmp2 * fjac[i-1][j][k][2][4]
	  - tmp1 * njac[i-1][j][k][2][4];
	lhs[i][j][k][AA][3][0] = - tmp2 * fjac[i-1][j][k][3][0]
	  - tmp1 * njac[i-1][j][k][3][0];
	lhs[i][j][k][AA][3][1] = - tmp2 * fjac[i-1][j][k][3][1]
	  - tmp1 * njac[i-1][j][k][3][1];
	lhs[i][j][k][AA][3][2] = - tmp2 * fjac[i-1][j][k][3][2]
	  - tmp1 * njac[i-1][j][k][3][2];
	lhs[i][j][k][AA][3][3] = - tmp2 * fjac[i-1][j][k][3][3]
	  - tmp1 * njac[i-1][j][k][3][3]
	  - tmp1 * dx4;
	lhs[i][j][k][AA][3][4] = - tmp2 * fjac[i-1][j][k][3][4]
	  - tmp1 * njac[i-1][j][k][3][4];
	lhs[i][j][k][AA][4][0] = - tmp2 * fjac[i-1][j][k][4][0]
	  - tmp1 * njac[i-1][j][k][4][0];
	lhs[i][j][k][AA][4][1] = - tmp2 * fjac[i-1][j][k][4][1]
	  - tmp1 * njac[i-1][j][k][4][1];
	lhs[i][j][k][AA][4][2] = - tmp2 * fjac[i-1][j][k][4][2]
	  - tmp1 * njac[i-1][j][k][4][2];
	lhs[i][j][k][AA][4][3] = - tmp2 * fjac[i-1][j][k][4][3]
	  - tmp1 * njac[i-1][j][k][4][3];
	lhs[i][j][k][AA][4][4] = - tmp2 * fjac[i-1][j][k][4][4]
	  - tmp1 * njac[i-1][j][k][4][4]
	  - tmp1 * dx5;
	lhs[i][j][k][BB][0][0] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][0][0]
	  + tmp1 * 2.0 * dx1;
	lhs[i][j][k][BB][0][1] = tmp1 * 2.0 * njac[i][j][k][0][1];
	lhs[i][j][k][BB][0][2] = tmp1 * 2.0 * njac[i][j][k][0][2];
	lhs[i][j][k][BB][0][3] = tmp1 * 2.0 * njac[i][j][k][0][3];
	lhs[i][j][k][BB][0][4] = tmp1 * 2.0 * njac[i][j][k][0][4];
	lhs[i][j][k][BB][1][0] = tmp1 * 2.0 * njac[i][j][k][1][0];
	lhs[i][j][k][BB][1][1] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][1][1]
	  + tmp1 * 2.0 * dx2;
	lhs[i][j][k][BB][1][2] = tmp1 * 2.0 * njac[i][j][k][1][2];
	lhs[i][j][k][BB][1][3] = tmp1 * 2.0 * njac[i][j][k][1][3];
	lhs[i][j][k][BB][1][4] = tmp1 * 2.0 * njac[i][j][k][1][4];
	lhs[i][j][k][BB][2][0] = tmp1 * 2.0 * njac[i][j][k][2][0];
	lhs[i][j][k][BB][2][1] = tmp1 * 2.0 * njac[i][j][k][2][1];
	lhs[i][j][k][BB][2][2] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][2][2]
	  + tmp1 * 2.0 * dx3;
	lhs[i][j][k][BB][2][3] = tmp1 * 2.0 * njac[i][j][k][2][3];
	lhs[i][j][k][BB][2][4] = tmp1 * 2.0 * njac[i][j][k][2][4];
	lhs[i][j][k][BB][3][0] = tmp1 * 2.0 * njac[i][j][k][3][0];
	lhs[i][j][k][BB][3][1] = tmp1 * 2.0 * njac[i][j][k][3][1];
	lhs[i][j][k][BB][3][2] = tmp1 * 2.0 * njac[i][j][k][3][2];
	lhs[i][j][k][BB][3][3] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][3][3]
	  + tmp1 * 2.0 * dx4;
	lhs[i][j][k][BB][3][4] = tmp1 * 2.0 * njac[i][j][k][3][4];
	lhs[i][j][k][BB][4][0] = tmp1 * 2.0 * njac[i][j][k][4][0];
	lhs[i][j][k][BB][4][1] = tmp1 * 2.0 * njac[i][j][k][4][1];
	lhs[i][j][k][BB][4][2] = tmp1 * 2.0 * njac[i][j][k][4][2];
	lhs[i][j][k][BB][4][3] = tmp1 * 2.0 * njac[i][j][k][4][3];
	lhs[i][j][k][BB][4][4] = 1.0
	  + tmp1 * 2.0 * njac[i][j][k][4][4]
	  + tmp1 * 2.0 * dx5;
	lhs[i][j][k][CC][0][0] =  tmp2 * fjac[i+1][j][k][0][0]
	  - tmp1 * njac[i+1][j][k][0][0]
	  - tmp1 * dx1;
	lhs[i][j][k][CC][0][1] =  tmp2 * fjac[i+1][j][k][0][1]
	  - tmp1 * njac[i+1][j][k][0][1];
	lhs[i][j][k][CC][0][2] =  tmp2 * fjac[i+1][j][k][0][2]
	  - tmp1 * njac[i+1][j][k][0][2];
	lhs[i][j][k][CC][0][3] =  tmp2 * fjac[i+1][j][k][0][3]
	  - tmp1 * njac[i+1][j][k][0][3];
	lhs[i][j][k][CC][0][4] =  tmp2 * fjac[i+1][j][k][0][4]
	  - tmp1 * njac[i+1][j][k][0][4];
	lhs[i][j][k][CC][1][0] =  tmp2 * fjac[i+1][j][k][1][0]
	  - tmp1 * njac[i+1][j][k][1][0];
	lhs[i][j][k][CC][1][1] =  tmp2 * fjac[i+1][j][k][1][1]
	  - tmp1 * njac[i+1][j][k][1][1]
	  - tmp1 * dx2;
	lhs[i][j][k][CC][1][2] =  tmp2 * fjac[i+1][j][k][1][2]
	  - tmp1 * njac[i+1][j][k][1][2];
	lhs[i][j][k][CC][1][3] =  tmp2 * fjac[i+1][j][k][1][3]
	  - tmp1 * njac[i+1][j][k][1][3];
	lhs[i][j][k][CC][1][4] =  tmp2 * fjac[i+1][j][k][1][4]
	  - tmp1 * njac[i+1][j][k][1][4];
	lhs[i][j][k][CC][2][0] =  tmp2 * fjac[i+1][j][k][2][0]
	  - tmp1 * njac[i+1][j][k][2][0];
	lhs[i][j][k][CC][2][1] =  tmp2 * fjac[i+1][j][k][2][1]
	  - tmp1 * njac[i+1][j][k][2][1];
	lhs[i][j][k][CC][2][2] =  tmp2 * fjac[i+1][j][k][2][2]
	  - tmp1 * njac[i+1][j][k][2][2]
	  - tmp1 * dx3;
	lhs[i][j][k][CC][2][3] =  tmp2 * fjac[i+1][j][k][2][3]
	  - tmp1 * njac[i+1][j][k][2][3];
	lhs[i][j][k][CC][2][4] =  tmp2 * fjac[i+1][j][k][2][4]
	  - tmp1 * njac[i+1][j][k][2][4];
	lhs[i][j][k][CC][3][0] =  tmp2 * fjac[i+1][j][k][3][0]
	  - tmp1 * njac[i+1][j][k][3][0];
	lhs[i][j][k][CC][3][1] =  tmp2 * fjac[i+1][j][k][3][1]
	  - tmp1 * njac[i+1][j][k][3][1];
	lhs[i][j][k][CC][3][2] =  tmp2 * fjac[i+1][j][k][3][2]
	  - tmp1 * njac[i+1][j][k][3][2];
	lhs[i][j][k][CC][3][3] =  tmp2 * fjac[i+1][j][k][3][3]
	  - tmp1 * njac[i+1][j][k][3][3]
	  - tmp1 * dx4;
	lhs[i][j][k][CC][3][4] =  tmp2 * fjac[i+1][j][k][3][4]
	  - tmp1 * njac[i+1][j][k][3][4];
	lhs[i][j][k][CC][4][0] =  tmp2 * fjac[i+1][j][k][4][0]
	  - tmp1 * njac[i+1][j][k][4][0];
	lhs[i][j][k][CC][4][1] =  tmp2 * fjac[i+1][j][k][4][1]
	  - tmp1 * njac[i+1][j][k][4][1];
	lhs[i][j][k][CC][4][2] =  tmp2 * fjac[i+1][j][k][4][2]
	  - tmp1 * njac[i+1][j][k][4][2];
	lhs[i][j][k][CC][4][3] =  tmp2 * fjac[i+1][j][k][4][3]
	  - tmp1 * njac[i+1][j][k][4][3];
	lhs[i][j][k][CC][4][4] =  tmp2 * fjac[i+1][j][k][4][4]
	  - tmp1 * njac[i+1][j][k][4][4]
	  - tmp1 * dx5;
      }
    }
  }
}
static void z_solve(void) {
  lhsz();
  z_solve_cell();
  z_backsubstitute();
}
static void z_backsubstitute(void) {
  int i, j, k, m, n;
#pragma omp parallel for private(j, k, m, n)
  for (i = 1; i < grid_points[0]-1; i++) {
    for (j = 1; j < grid_points[1]-1; j++) {
      for (k = grid_points[2]-2; k >= 0; k--) {
	for (m = 0; m < BLOCK_SIZE; m++) {
	  for (n = 0; n < BLOCK_SIZE; n++) {
	    rhs[i][j][k][m] = rhs[i][j][k][m] 
	      - lhs[i][j][k][CC][m][n]*rhs[i][j][k+1][n];
	  }
	}
      }
    }
  }
}
static void z_solve_cell(void) {
  int i,j,k,ksize;
  ksize = grid_points[2]-1;
#pragma omp parallel for private(j)
  for (i = 1; i < grid_points[0]-1; i++) {
    for (j = 1; j < grid_points[1]-1; j++) {
      binvcrhs( lhs[i][j][0][BB],
		lhs[i][j][0][CC],
		rhs[i][j][0] );
    }
  }
  for (k = 1; k < ksize; k++) {
#pragma omp parallel for private(j)
      for (i = 1; i < grid_points[0]-1; i++) {
	  for (j = 1; j < grid_points[1]-1; j++) {
	matvec_sub(lhs[i][j][k][AA],
		   rhs[i][j][k-1], rhs[i][j][k]);
	matmul_sub(lhs[i][j][k][AA],
		   lhs[i][j][k-1][CC],
		   lhs[i][j][k][BB]);
	binvcrhs( lhs[i][j][k][BB],
		  lhs[i][j][k][CC],
		  rhs[i][j][k] );
      }
    }
  }
#pragma omp parallel for private(j)
  for (i = 1; i < grid_points[0]-1; i++) {
    for (j = 1; j < grid_points[1]-1; j++) {
      matvec_sub(lhs[i][j][ksize][AA],
		 rhs[i][j][ksize-1], rhs[i][j][ksize]);
      matmul_sub(lhs[i][j][ksize][AA],
		 lhs[i][j][ksize-1][CC],
		 lhs[i][j][ksize][BB]);
      binvrhs( lhs[i][j][ksize][BB],
	       rhs[i][j][ksize] );
    }
  }
}