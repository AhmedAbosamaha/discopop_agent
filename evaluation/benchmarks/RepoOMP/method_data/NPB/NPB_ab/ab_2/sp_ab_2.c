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
  for (i = 0; i <= IMAX-1; i++) {
    for (j = 0; j <= IMAX-1; j++) {
      for (k = 0; k <= IMAX-1; k++) {
        u[0][i][j][k] = 1.0;
        u[1][i][j][k] = 0.0;
        u[2][i][j][k] = 0.0;
        u[3][i][j][k] = 0.0;
        u[4][i][j][k] = 1.0;
      }
    }
  }
  for (j = 0; j < grid_points[1]; j++) {
    double temp[5], xi, eta, zeta; 
    xi = 0.0;
    eta = (double)j * dnym1;
    for (k = 0; k < grid_points[2]; k++) {
      zeta = (double)k * dnzm1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) { u[m][i][j][k] = temp[m]; }
    }
  }
  i = grid_points[0]-1;
  for (i = 0; i < grid_points[0]; i++) {
    double temp[5], xi, eta, zeta; 
    eta = 0.0;
    xi = (double)i * dnxm1;
    for (k = 0; k < grid_points[2]; k++) {
      zeta = (double)k * dnzm1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) { u[m][i][j][k] = temp[m]; }
    }
  }
  j = grid_points[1]-1;
  for (i = 0; i < grid_points[0]; i++) {
    double temp[5], xi, eta, zeta; 
    zeta = 0.0;
    xi = (double)i * dnxm1;
    for (j = 0; j < grid_points[1]; j++) {
      eta = (double)j * dnym1;
      exact_solution(xi, eta, zeta, temp);
      for (m = 0; m < 5; m++) { u[m][i][j][k] = temp[m]; }
    }
  }
  k = grid_points[2]-1;
  for (j = 1; j <= grid_points[1]-2; j++) {
    double cv[IMAX], rhon[IMAX]; 
    for (k = 1; k <= grid_points[2]-2; k++) {
      for (i = 0; i <= grid_points[0]-1; i++) {
        ru1 = c3c4*rho_i[i][j][k];
        cv[i] = us[i][j][k];
        rhon[i] = max(dx2+con43*ru1, 
                  max(dx5+c1c5*ru1,
                  max(dxmax+ru1,
                      dx1)));
      }
      for (i = 1; i <= grid_points[0]-2; i++) {
        lhs[0][i][j][k] =   0.0;
        lhs[1][i][j][k] = - dttx2 * cv[i-1] - dttx1 * rhon[i-1];
        lhs[2][i][j][k] =   1.0 + c2dttx1 * rhon[i];
        lhs[3][i][j][k] =   dttx2 * cv[i+1] - dttx1 * rhon[i+1];
        lhs[4][i][j][k] =   0.0;
      }
    }
  }
  i = 1;
  for (i = 3; i <= grid_points[0]-4; i++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        lhs[0][i][j][k] = lhs[0][i][j][k] + comz1;
        lhs[1][i][j][k] = lhs[1][i][j][k] - comz4;
        lhs[2][i][j][k] = lhs[2][i][j][k] + comz6;
        lhs[3][i][j][k] = lhs[3][i][j][k] - comz4;
        lhs[4][i][j][k] = lhs[4][i][j][k] + comz1;
      }
    }
  }
  i = grid_points[0]-3;
  for (i = 1; i <= grid_points[0]-2; i++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        lhs[0+5][i][j][k]  = lhs[0][i][j][k];
        lhs[1+5][i][j][k]  = lhs[1][i][j][k] - dttx2 * speed[i-1][j][k];
        lhs[2+5][i][j][k]  = lhs[2][i][j][k];
        lhs[3+5][i][j][k]  = lhs[3][i][j][k] + dttx2 * speed[i+1][j][k];
        lhs[4+5][i][j][k]  = lhs[4][i][j][k];
        lhs[0+10][i][j][k] = lhs[0][i][j][k];
        lhs[1+10][i][j][k] = lhs[1][i][j][k] + dttx2 * speed[i-1][j][k];
        lhs[2+10][i][j][k] = lhs[2][i][j][k];
        lhs[3+10][i][j][k] = lhs[3][i][j][k] - dttx2 * speed[i+1][j][k];
        lhs[4+10][i][j][k] = lhs[4][i][j][k];
      }
    }
  }
}
static void lhsy(void) {
  double ru1;
  int i, j, k;
  for (i = 1; i <= grid_points[0]-2; i++) {
    for (k = 1; k <= grid_points[2]-2; k++) {
      lhs[2][i][j][k] = lhs[2][i][j][k] + comz5;
      lhs[3][i][j][k] = lhs[3][i][j][k] - comz4;
      lhs[4][i][j][k] = lhs[4][i][j][k] + comz1;
      lhs[1][i][j+1][k] = lhs[1][i][j+1][k] - comz4;
      lhs[2][i][j+1][k] = lhs[2][i][j+1][k] + comz6;
      lhs[3][i][j+1][k] = lhs[3][i][j+1][k] - comz4;
      lhs[4][i][j+1][k] = lhs[4][i][j+1][k] + comz1;
    }
  }
  for (i = 1; i <= grid_points[0]-2; i++) {
    for (k = 1; k <= grid_points[2]-2; k++) {
      lhs[0][i][j][k] = lhs[0][i][j][k] + comz1;
      lhs[1][i][j][k] = lhs[1][i][j][k] - comz4;
      lhs[2][i][j][k] = lhs[2][i][j][k] + comz6;
      lhs[3][i][j][k] = lhs[3][i][j][k] - comz4;
      lhs[0][i][j+1][k] = lhs[0][i][j+1][k] + comz1;
      lhs[1][i][j+1][k] = lhs[1][i][j+1][k] - comz4;
      lhs[2][i][j+1][k] = lhs[2][i][j+1][k] + comz5;
    }
  }
  for (i = 1; i <= grid_points[0]-2; i++) {
    double cv[KMAX], rhos[KMAX];
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 0; k <= grid_points[2]-1; k++) {
        ru1 = c3c4*rho_i[i][j][k];
        cv[k] = ws[i][j][k];
        rhos[k] = max(dz4 + con43 * ru1,
                  max(dz5 + c1c5 * ru1,
                  max(dzmax + ru1,
                      dz1)));
      }
      for (k = 1; k <= grid_points[2]-2; k++) {
        lhs[0][i][j][k] =  0.0;
        lhs[1][i][j][k] = -dttz2 * cv[k-1] - dttz1 * rhos[k-1];
        lhs[2][i][j][k] =  1.0 + c2dttz1 * rhos[k];
        lhs[3][i][j][k] =  dttz2 * cv[k+1] - dttz1 * rhos[k+1];
        lhs[4][i][j][k] =  0.0;
      }
    }
  }
  k = 1;
  for (i = 1; i <= grid_points[0]-2; i++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 3; k <= grid_points[2]-4; k++) {
        lhs[0][i][j][k] = lhs[0][i][j][k] + comz1;
        lhs[1][i][j][k] = lhs[1][i][j][k] - comz4;
        lhs[2][i][j][k] = lhs[2][i][j][k] + comz6;
        lhs[3][i][j][k] = lhs[3][i][j][k] - comz4;
        lhs[4][i][j][k] = lhs[4][i][j][k] + comz1;
      }
    }
  }
  k = grid_points[2]-3;
  for (i = 1; i <= grid_points[0]-2; i++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        lhs[0+5][i][j][k]  = lhs[0][i][j][k];
        lhs[1+5][i][j][k]  = lhs[1][i][j][k] - dttz2 * speed[i][j][k-1];
        lhs[2+5][i][j][k]  = lhs[2][i][j][k];
        lhs[3+5][i][j][k]  = lhs[3][i][j][k] + dttz2 * speed[i][j][k+1];
        lhs[4+5][i][j][k]  = lhs[4][i][j][k];
        lhs[0+10][i][j][k] = lhs[0][i][j][k];
        lhs[1+10][i][j][k] = lhs[1][i][j][k] + dttz2 * speed[i][j][k-1];  
        lhs[2+10][i][j][k] = lhs[2][i][j][k];
        lhs[3+10][i][j][k] = lhs[3][i][j][k] - dttz2 * speed[i][j][k+1];  
        lhs[4+10][i][j][k] = lhs[4][i][j][k];
      }
    }
  }
}
static void ninvr(void) {
  int i, j, k;
  double r1, r2, r3, r4, r5, t1, t2;
  for (j = 1; j <= grid_points[1]-2; j++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        r1 = rhs[0][i][j][k];
        r2 = rhs[1][i][j][k];
        r3 = rhs[2][i][j][k];
        r4 = rhs[3][i][j][k];
        r5 = rhs[4][i][j][k];
        t1 = bt * r1;
        t2 = 0.5 * ( r4 + r5 );
        rhs[0][i][j][k] =  bt * ( r4 - r5 );
        rhs[1][i][j][k] = -r3;
        rhs[2][i][j][k] =  r2;
        rhs[3][i][j][k] = -t1 + t2;
        rhs[4][i][j][k] =  t1 + t2;
      }
    }
  }
}
#include <math.h>
#include "omp.h"
static void compute_rhs(void) {
  int i, j, k, m;
  double aux, rho_inv, uijk, up1, um1, vijk, vp1, vm1,
    wijk, wp1, wm1;
  for (j = 0; j <= grid_points[1]-1; j++) {
    for (m = 0; m < 5; m++) {
      for (i = 0; i <= grid_points[0]-1; i++) {
        for (k = 0; k <= grid_points[2]-1; k++) {
          rhs[m][i][j][k] = forcing[m][i][j][k];
        }
      }
    }
  }
#pragma omp parallel for collapse(2) private(i, k, uijk, up1, um1) schedule(dynamic)
  for (j = 1; j <= grid_points[1]-2; j++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        uijk = us[i][j][k];
        up1  = us[i+1][j][k];
        um1  = us[i-1][j][k];
        rhs[0][i][j][k] = rhs[0][i][j][k] + dx1tx1 * (u[0][i+1][j][k] - 2.0*u[0][i][j][k] + u[0][i-1][j][k]) - tx2 * (u[1][i+1][j][k] - u[1][i-1][j][k]);
        rhs[1][i][j][k] = rhs[1][i][j][k] + dx2tx1 * (u[1][i+1][j][k] - 2.0*u[1][i][j][k] + u[1][i-1][j][k]) + xxcon2*con43 * (up1 - 2.0*uijk + um1) - tx2 * (u[1][i+1][j][k]*up1 - u[1][i-1][j][k]*um1 + (u[4][i+1][j][k]- square[i+1][j][k]- u[4][i-1][j][k]+ square[i-1][j][k])*c2);
        rhs[2][i][j][k] = rhs[2][i][j][k] + dx3tx1 * (u[2][i+1][j][k] - 2.0*u[2][i][j][k] + u[2][i-1][j][k]) + xxcon2 * (vs[i+1][j][k] - 2.0*vs[i][j][k] + vs[i-1][j][k]) - tx2 * (u[2][i+1][j][k]*up1 - u[2][i-1][j][k]*um1);
        rhs[3][i][j][k] = rhs[3][i][j][k] + dx4tx1 * (u[3][i+1][j][k] - 2.0*u[3][i][j][k] + u[3][i-1][j][k]) + xxcon2 * (ws[i+1][j][k] - 2.0*ws[i][j][k] + ws[i-1][j][k]) - tx2 * (u[3][i+1][j][k]*up1 - u[3][i-1][j][k]*um1);
        rhs[4][i][j][k] = rhs[4][i][j][k] + dx5tx1 * (u[4][i+1][j][k] - 2.0*u[4][i][j][k] + u[4][i-1][j][k]) + xxcon3 * (qs[i+1][j][k] - 2.0*qs[i][j][k] + qs[i-1][j][k]) + xxcon4 * (up1*up1 - 2.0*uijk*uijk + um1*um1) + xxcon5 * (u[4][i+1][j][k]*rho_i[i+1][j][k] - 2.0*u[4][i][j][k]*rho_i[i][j][k] + u[4][i-1][j][k]*rho_i[i-1][j][k]) - tx2 * ( (c1*u[4][i+1][j][k] - c2*square[i+1][j][k])*up1 - (c1*u[4][i-1][j][k] - c2*square[i-1][j][k])*um1 );
      }
    }
  }
  i = 1;
  for (m = 0; m < 5; m++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - dssp * (-4.0*u[m][i-1][j][k] + 6.0*u[m][i][j][k] - 4.0*u[m][i+1][j][k] + u[m][i+2][j][k]);
      }
    }
  }
  for (m = 0; m < 5; m++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - dssp * ( u[m][i-2][j][k] - 4.0*u[m][i-1][j][k] + 6.0*u[m][i][j][k] - 4.0*u[m][i+1][j][k] );
      }
    }
  }
  i = grid_points[0]-2;
  for (j = 1; j <= grid_points[1]-2; j++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        vijk = vs[i][j][k];
        vp1  = vs[i][j+1][k];
        vm1  = vs[i][j-1][k];
        rhs[0][i][j][k] = rhs[0][i][j][k] + dy1ty1 * (u[0][i][j+1][k] - 2.0*u[0][i][j][k] + u[0][i][j-1][k]) - ty2 * (u[2][i][j+1][k] - u[2][i][j-1][k]);
        rhs[1][i][j][k] = rhs[1][i][j][k] + dy2ty1 * (u[1][i][j+1][k] - 2.0*u[1][i][j][k] + u[1][i][j-1][k]) + yycon2 * (us[i][j+1][k] - 2.0*us[i][j][k] + us[i][j-1][k]) - ty2 * (u[1][i][j+1][k]*vp1 - u[1][i][j-1][k]*vm1);
        rhs[2][i][j][k] = rhs[2][i][j][k] + dy3ty1 * (u[2][i][j+1][k] - 2.0*u[2][i][j][k] + u[2][i][j-1][k]) + yycon2*con43 * (vp1 - 2.0*vijk + vm1) - ty2 * (u[2][i][j+1][k]*vp1 - u[2][i][j-1][k]*vm1 + (u[4][i][j+1][k] - square[i][j+1][k] - u[4][i][j-1][k] + square[i][j-1][k]) *c2);
        rhs[3][i][j][k] = rhs[3][i][j][k] + dy4ty1 * (u[3][i][j+1][k] - 2.0*u[3][i][j][k] + u[3][i][j-1][k]) + yycon2 * (ws[i][j+1][k] - 2.0*ws[i][j][k] + ws[i][j-1][k]) - ty2 * (u[3][i][j+1][k]*vp1 - u[3][i][j-1][k]*vm1);
        rhs[4][i][j][k] = rhs[4][i][j][k] + dy5ty1 * (u[4][i][j+1][k] - 2.0*u[4][i][j][k] + u[4][i][j-1][k]) + yycon3 * (qs[i][j+1][k] - 2.0*qs[i][j][k] + qs[i][j-1][k]) + yycon4 * (vp1*vp1 - 2.0*vijk*vijk + vm1*vm1) + yycon5 * (u[4][i][j+1][k]*rho_i[i][j+1][k] - 2.0*u[4][i][j][k]*rho_i[i][j][k] + u[4][i][j-1][k]*rho_i[i][j-1][k]) - ty2 * ((c1*u[4][i][j+1][k] - c2*square[i][j+1][k]) * vp1 - (c1*u[4][i][j-1][k] - c2*square[i][j-1][k]) * vm1);
      }
    }
  }
  j = 1;
  for (m = 0; m < 5; m++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - dssp * (-4.0*u[m][i][j-1][k] + 6.0*u[m][i][j][k] - 4.0*u[m][i][j+1][k] + u[m][i][j+2][k]);
      }
    }
  }
  for (m = 0; m < 5; m++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - dssp * ( u[m][i][j-2][k] - 4.0*u[m][i][j-1][k] + 6.0*u[m][i][j][k] - 4.0*u[m][i][j+1][k] );
      }
    }
  }
  j = grid_points[1]-2;
  for (j = 1; j <= grid_points[1]-2; j++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        wijk = ws[i][j][k];
        wp1  = ws[i][j][k+1];
        wm1  = ws[i][j][k-1];
        rhs[0][i][j][k] = rhs[0][i][j][k] + dz1tz1 * (u[0][i][j][k+1] - 2.0*u[0][i][j][k] + u[0][i][j][k-1]) - tz2 * (u[3][i][j][k+1] - u[3][i][j][k-1]);
        rhs[1][i][j][k] = rhs[1][i][j][k] + dz2tz1 * (u[1][i][j][k+1] - 2.0*u[1][i][j][k] + u[1][i][j][k-1]) + zzcon2 * (us[i][j][k+1] - 2.0*us[i][j][k] + us[i][j][k-1]) - tz2 * (u[1][i][j][k+1]*wp1 - u[1][i][j][k-1]*wm1);
        rhs[2][i][j][k] = rhs[2][i][j][k] + dz3tz1 * (u[2][i][j][k+1] - 2.0*u[2][i][j][k] + u[2][i][j][k-1]) + zzcon2 * (vs[i][j][k+1] - 2.0*vs[i][j][k] + vs[i][j][k-1]) - tz2 * (u[2][i][j][k+1]*wp1 - u[2][i][j][k-1]*wm1);
        rhs[3][i][j][k] = rhs[3][i][j][k] + dz4tz1 * (u[3][i][j][k+1] - 2.0*u[3][i][j][k] + u[3][i][j][k-1]) + zzcon2*con43 * (wp1 - 2.0*wijk + wm1) - tz2 * (u[3][i][j][k+1]*wp1 - u[3][i][j][k-1]*wm1 + (u[4][i][j][k+1] - square[i][j][k+1] - u[4][i][j][k-1] + square[i][j][k-1]) *c2);
        rhs[4][i][j][k] = rhs[4][i][j][k] + dz5tz1 * (u[4][i][j][k+1] - 2.0*u[4][i][j][k] + u[4][i][j][k-1]) + zzcon3 * (qs[i][j][k+1] - 2.0*qs[i][j][k] + qs[i][j][k-1]) + zzcon4 * (wp1*wp1 - 2.0*wijk*wijk + wm1*wm1) + zzcon5 * (u[4][i][j][k+1]*rho_i[i][j][k+1] - 2.0*u[4][i][j][k]*rho_i[i][j][k] + u[4][i][j][k-1]*rho_i[i][j][k-1]) - tz2 * ( (c1*u[4][i][j][k+1] - c2*square[i][j][k+1])*wp1 - (c1*u[4][i][j][k-1] - c2*square[i][j][k-1])*wm1);
      }
    }
  }
  k = 1;
  for (m = 0; m < 5; m++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = 1; j <= grid_points[1]-2; j++) {
        for (k = 3; k <= grid_points[2]-4; k++) {
          rhs[m][i][j][k] = rhs[m][i][j][k] - dssp * ( u[m][i][j][k-2] - 4.0*u[m][i][j][k-1] + 6.0*u[m][i][j][k] - 4.0*u[m][i][j][k+1] + u[m][i][j][k+2] );
        }
      }
    }
  }
  k = grid_points[2]-3;
  for (m = 0; m < 5; m++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = 1; j <= grid_points[1]-2; j++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - dssp * ( u[m][i][j][k-2] - 4.0*u[m][i][j][k-1] + 5.0*u[m][i][j][k] );
      }
    }
  }
  for (j = 1; j <= grid_points[1]-2; j++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        ru1 = rho_i[i][j][k];
        uu = us[i][j][k];
        vv = vs[i][j][k];
        ww = ws[i][j][k];
        ac = speed[i][j][k];
        ac2inv = ainv[i][j][k]*ainv[i][j][k];
        r1 = rhs[0][i][j][k];
        r2 = rhs[1][i][j][k];
        r3 = rhs[2][i][j][k];
        r4 = rhs[3][i][j][k];
        r5 = rhs[4][i][j][k];
        t1 = c2 * ac2inv * ( qs[i][j][k]*r1 - uu*r2  - 
                     vv*r3 - ww*r4 + r5 );
        t2 = bt * ru1 * ( uu * r1 - r2 );
        t3 = ( bt * ru1 * ac ) * t1;
        rhs[0][i][j][k] = r1 - t1;
        rhs[1][i][j][k] = - ru1 * ( ww*r1 - r4 );
        rhs[2][i][j][k] =   ru1 * ( vv*r1 - r3 );
        rhs[3][i][j][k] = - t2 + t3;
        rhs[4][i][j][k] =   t2 + t3;
      }
    }
  }
}
static void tzetar(void) {
  int i, j, k;
  double t1, t2, t3, ac, xvel, yvel, zvel, r1, r2, r3, 
    r4, r5, btuz, acinv, ac2u, uzik1;
  for (j = 1; j <= grid_points[1]-2; j++) {
    for (i = 0; i <= grid_points[0]-3; i++) {
      i1 = i  + 1;
      i2 = i  + 2;
      for (k = 1; k <= grid_points[2]-2; k++) {
        fac1 = 1./lhs[n+2][i][j][k];
        lhs[n+3][i][j][k] = fac1*lhs[n+3][i][j][k];
        lhs[n+4][i][j][k] = fac1*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i][j][k] = fac1*rhs[m][i][j][k]; }
        lhs[n+2][i1][j][k] = lhs[n+2][i1][j][k] - lhs[n+1][i1][j][k]*lhs[n+3][i][j][k];
        lhs[n+3][i1][j][k] = lhs[n+3][i1][j][k] - lhs[n+1][i1][j][k]*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i1][j][k] = rhs[m][i1][j][k] - lhs[n+1][i1][j][k]*rhs[m][i][j][k]; }
        lhs[n+1][i2][j][k] = lhs[n+1][i2][j][k] - lhs[n+0][i2][j][k]*lhs[n+3][i][j][k];
        lhs[n+2][i2][j][k] = lhs[n+2][i2][j][k] - lhs[n+0][i2][j][k]*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i2][j][k] = rhs[m][i2][j][k] - lhs[n+0][i2][j][k]*rhs[m][i][j][k]; }
      }
    }
  }
  i  = grid_points[0]-2;
  i1 = grid_points[0]-1;
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (i = 0; i <= grid_points[0]-3; i++) {
        i1 = i  + 1;
        i2 = i  + 2;
        for (k = 1; k <= grid_points[2]-2; k++) {
          fac1 = 1./lhs[n+2][i][j][k];
          lhs[n+3][i][j][k] = fac1*lhs[n+3][i][j][k];
          lhs[n+4][i][j][k] = fac1*lhs[n+4][i][j][k];
          rhs[m][i][j][k] = fac1*rhs[m][i][j][k];
          lhs[n+2][i1][j][k] = lhs[n+2][i1][j][k] - lhs[n+1][i1][j][k]*lhs[n+3][i][j][k];
          lhs[n+3][i1][j][k] = lhs[n+3][i1][j][k] - lhs[n+1][i1][j][k]*lhs[n+4][i][j][k];
          rhs[m][i1][j][k] = rhs[m][i1][j][k] - lhs[n+1][i1][j][k]*rhs[m][i][j][k];
          lhs[n+1][i2][j][k] = lhs[n+1][i2][j][k] - lhs[n+0][i2][j][k]*lhs[n+3][i][j][k];
          lhs[n+2][i2][j][k] = lhs[n+2][i2][j][k] - lhs[n+0][i2][j][k]*lhs[n+4][i][j][k];
          rhs[m][i2][j][k] = rhs[m][i2][j][k] - lhs[n+0][i2][j][k]*rhs[m][i][j][k];
        }
      }
    }
    i  = grid_points[0]-2;
    i1 = grid_points[0]-1;
  for (m = 0; m < 3; m++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - lhs[n+3][i][j][k]*rhs[m][i1][j][k];
      }
    }
  }
  for (j = 1; j <= grid_points[1]-2; j++) {
    for (m = 0; m < 3; m++) {
      for (i = grid_points[0]-3; i >= 0; i--) {
        i1 = i  + 1;
        i2 = i  + 2;
        for (k = 1; k <= grid_points[2]-2; k++) {
          rhs[m][i][j][k] = rhs[m][i][j][k] - lhs[n+3][i][j][k]*rhs[m][i1][j][k] - lhs[n+4][i][j][k]*rhs[m][i2][j][k];
        }
      }
    }
  }
  for (i = 1; i <= grid_points[0]-2; i++) {
    for (j = 0; j <= grid_points[1]-3; j++) {
      j1 = j  + 1;
      j2 = j  + 2;
      for (k = 1; k <= grid_points[2]-2; k++) {
        fac1 = 1./lhs[n+2][i][j][k];
        lhs[n+3][i][j][k] = fac1*lhs[n+3][i][j][k];
        lhs[n+4][i][j][k] = fac1*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i][j][k] = fac1*rhs[m][i][j][k]; }
        lhs[n+2][i][j1][k] = lhs[n+2][i][j1][k] - lhs[n+1][i][j1][k]*lhs[n+3][i][j][k];
        lhs[n+3][i][j1][k] = lhs[n+3][i][j1][k] - lhs[n+1][i][j1][k]*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i][j1][k] = rhs[m][i][j1][k] - lhs[n+1][i][j1][k]*rhs[m][i][j][k]; }
        lhs[n+1][i][j2][k] = lhs[n+1][i][j2][k] - lhs[n+0][i][j2][k]*lhs[n+3][i][j][k];
        lhs[n+2][i][j2][k] = lhs[n+2][i][j2][k] - lhs[n+0][i][j2][k]*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i][j2][k] = rhs[m][i][j2][k] - lhs[n+0][i][j2][k]*rhs[m][i][j][k]; }
      }
    }
  }
  j  = grid_points[1]-2;
  j1 = grid_points[1]-1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = 0; j <= grid_points[1]-3; j++) {
        j1 = j  + 1;
        j2 = j  + 2;
        for (k = 1; k <= grid_points[2]-2; k++) {
          fac1 = 1./lhs[n+2][i][j][k];
          lhs[n+3][i][j][k] = fac1*lhs[n+3][i][j][k];
          lhs[n+4][i][j][k] = fac1*lhs[n+4][i][j][k];
          rhs[m][i][j][k] = fac1*rhs[m][i][j][k];
          lhs[n+2][i][j1][k] = lhs[n+2][i][j1][k] - lhs[n+1][i][j1][k]*lhs[n+3][i][j][k];
          lhs[n+3][i][j1][k] = lhs[n+3][i][j1][k] - lhs[n+1][i][j1][k]*lhs[n+4][i][j][k];
          rhs[m][i][j1][k] = rhs[m][i][j1][k] - lhs[n+1][i][j1][k]*rhs[m][i][j][k];
          lhs[n+1][i][j2][k] = lhs[n+1][i][j2][k] - lhs[n+0][i][j2][k]*lhs[n+3][i][j][k];
          lhs[n+2][i][j2][k] = lhs[n+2][i][j2][k] - lhs[n+0][i][j2][k]*lhs[n+4][i][j][k];
          rhs[m][i][j2][k] = rhs[m][i][j2][k] - lhs[n+0][i][j2][k]*rhs[m][i][j][k];
        }
      }
    }
    j  = grid_points[1]-2;
    j1 = grid_points[1]-1;
  for (m = 0; m < 3; m++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (k = 1; k <= grid_points[2]-2; k++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - lhs[n+3][i][j][k]*rhs[m][i][j1][k];
      }
    }
  }
  for (m = 0; m < 3; m++) {
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = grid_points[1]-3; j >= 0; j--) {
        j1 = j  + 1;
        j2 = j  + 2;
        for (k = 1; k <= grid_points[2]-2; k++) {
          rhs[m][i][j][k] = rhs[m][i][j][k] - lhs[n+3][i][j][k]*rhs[m][i][j1][k] - lhs[n+4][i][j][k]*rhs[m][i][j2][k];
        }
      }
    }
  }
  for (i = 1; i <= grid_points[0]-2; i++) {
    for (j = 1; j <= grid_points[1]-2; j++) {
      for (k = 0; k <= grid_points[2]-3; k++) {
        k1 = k  + 1;
        k2 = k  + 2;
        fac1 = 1./lhs[n+2][i][j][k];
        lhs[n+3][i][j][k] = fac1*lhs[n+3][i][j][k];
        lhs[n+4][i][j][k] = fac1*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i][j][k] = fac1*rhs[m][i][j][k]; }
        lhs[n+2][i][j][k1] = lhs[n+2][i][j][k1] - lhs[n+1][i][j][k1]*lhs[n+3][i][j][k];
        lhs[n+3][i][j][k1] = lhs[n+3][i][j][k1] - lhs[n+1][i][j][k1]*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i][j][k1] = rhs[m][i][j][k1] - lhs[n+1][i][j][k1]*rhs[m][i][j][k]; }
        lhs[n+1][i][j][k2] = lhs[n+1][i][j][k2] - lhs[n+0][i][j][k2]*lhs[n+3][i][j][k];
        lhs[n+2][i][j][k2] = lhs[n+2][i][j][k2] - lhs[n+0][i][j][k2]*lhs[n+4][i][j][k];
        for (m = 0; m < 3; m++) { rhs[m][i][j][k2] = rhs[m][i][j][k2] - lhs[n+0][i][j][k2]*rhs[m][i][j][k]; }
      }
    }
  }
  k  = grid_points[2]-2;
  k1 = grid_points[2]-1;
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = 1; j <= grid_points[1]-2; j++) {
        fac1 = 1./lhs[n+2][i][j][k];
        lhs[n+3][i][j][k] = fac1*lhs[n+3][i][j][k];
        lhs[n+4][i][j][k] = fac1*lhs[n+4][i][j][k];
        rhs[m][i][j][k] = fac1*rhs[m][i][j][k];
        lhs[n+2][i][j][k1] = lhs[n+2][i][j][k1] - lhs[n+1][i][j][k1]*lhs[n+3][i][j][k];
        lhs[n+3][i][j][k1] = lhs[n+3][i][j][k1] - lhs[n+1][i][j][k1]*lhs[n+4][i][j][k];
        rhs[m][i][j][k1] = rhs[m][i][j][k1] - lhs[n+1][i][j][k1]*rhs[m][i][j][k];
        fac2 = 1./lhs[n+2][i][j][k1];
        rhs[m][i][j][k1] = fac2*rhs[m][i][j][k1];
      }
    }
  }
  k  = grid_points[2]-2;
  k1 = grid_points[2]-1;
  n = 0;
  for (m = 3; m < 5; m++) {
    n = (m-3+1)*5;
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = 1; j <= grid_points[1]-2; j++) {
        rhs[m][i][j][k] = rhs[m][i][j][k] - lhs[n+3][i][j][k]*rhs[m][i][j][k1];
      }
    }
  }
  n = 0;
  for (m = 3; m < 5; m++) {
    n = (m-3+1)*5;
    for (i = 1; i <= grid_points[0]-2; i++) {
      for (j = 1; j <= grid_points[1]-2; j++) {
        for (k = grid_points[2]-3; k >= 0; k--) {
          k1 = k  + 1;
          k2 = k  + 2;
          rhs[m][i][j][k] = rhs[m][i][j][k] - lhs[n+3][i][j][k]*rhs[m][i][j][k1] - lhs[n+4][i][j][k]*rhs[m][i][j][k2];
        }
      }
    }
  }
  tzetar();
}