#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include "npb-C.h"






int main(int argc, char **argv) {

  int i, j, k, it;
  double zeta;
  double rnorm;
  double d, rho, rho0;
  double alpha, beta;

  double t, mflops;

  char class;
  boolean verified;
  double zeta_verify_value, epsilon, err;

  char *t_names[16];

  if (argc == 1) {
    fprintf(stderr, "Usage: %s <inputfile>
", argv[0]);
    exit(1);
  }

  FILE *fp;
  if ((fp = fopen(argv[1], "r")) == NULL) {
    fprintf(stderr, "Input file %s does not exist
", argv[1]);
    exit(1);
  }

  if (fscanf(fp, "%d", &na) != 1) {
    fprintf(stderr, "error in reading na
");
    exit(1);
  }
  if (fscanf(fp, "%d", &niter) != 1) {
    fprintf(stderr, "error in reading niter
");
    exit(1);
  }
  if (fscanf(fp, "%lf", &zeta_verify_value) != 1) {
    fprintf(stderr, "error in reading zeta_verify_value
");
    exit(1);
  }
  if (fscanf(fp, "%d", &class) != 1) {
    fprintf(stderr, "error in reading class
");
    exit(1);
  }
  fclose(fp);

  
  
  
  x = (double*)malloc(sizeof(double)*(na+1));
  q = (double*)malloc(sizeof(double)*(na+1));
  r = (double*)malloc(sizeof(double)*(na+1));
  p = (double*)malloc(sizeof(double)*(na+1));
  a = (double*)malloc(sizeof(double)*(na*(NONZER+1)+1));
  colidx = (int*)malloc(sizeof(int)*(na*(NONZER+1)+1));
  rowstr = (int*)malloc(sizeof(int)*(na+2));

  
  
  
  makea(na, NONZER, a, colidx, rowstr, 0, nz, &rcond, &shift);

  
  
  
  #pragma omp parallel for private(i,j,k)
  for (j = 0; j < na+1; j++) {
    x[j] = 1.0;
    q[j] = 0.0;
    r[j] = 0.0;
    p[j] = 0.0;
  }

  zeta = 0.0;

  
  
  
  for (it = 1; it <= niter; it++) {
    
    
    
    #pragma omp parallel for private(j,k,sum,rnorm)
    for (j = 0; j < na; j++) {
      sum = 0.0;
      for (k = rowstr[j]; k < rowstr[j+1]; k++) {
        sum = sum + a[k] * p[colidx[k]];
      }
      q[j] = sum;
    }

    #pragma omp parallel for private(j) reduction(+:d)
    for (j = 0; j < na; j++) {
      d = d + p[j] * q[j];
    }

    alpha = rho0 / d;

    #pragma omp parallel for private(j)
    for (j = 0; j < na; j++) {
      x[j] = x[j] + alpha * p[j];
      r[j] = r[j] - alpha * q[j];
    }

    rho = 0.0;
    #pragma omp parallel for private(j) reduction(+:rho)
    for (j = 0; j < na; j++) {
      rho = rho + r[j] * r[j];
    }

    beta = rho / rho0;
    rho0 = rho;

    #pragma omp parallel for private(j)
    for (j = 0; j < na; j++) {
      p[j] = r[j] + beta * p[j];
    }

    if (it == 1) {
      rnorm = 0.0;
      #pragma omp parallel for private(j) reduction(+:rnorm)
      for (j = 0; j < na; j++) {
        rnorm = rnorm + r[j] * r[j];
      }
      rnorm = sqrt(rnorm);
    }

    
    
    
    zeta = shift + 1.0 / rho;
    if (it == 1) printf("
   iteration           ||r||                 zeta
");
    printf("    %5d       %20.14e%20.14e
", it, rnorm, zeta);
  }

  
  
  

  
  
  
  epsilon = 1.0e-10;
  err = fabs(zeta - zeta_verify_value) / zeta_verify_value;
  if (class != 'U') {
    if (err <= epsilon) {
      verified = TRUE;
      printf(" VERIFICATION SUCCESSFUL
");
      printf(" zeta = %16.12f
", zeta);
      printf(" Error is   %16.12f
", err);
    } else {
      verified = FALSE;
      printf(" VERIFICATION FAILED
");
      printf(" zeta = %16.12f
", zeta);
      printf(" The correct zeta is %16.12f
", zeta_verify_value);
    }
  } else {
    verified = FALSE;
    printf(" Problem size unknown
");
    printf(" NO VERIFICATION PERFORMED
");
  }

  
  
  
  if (timeron) {
    t = timer_read(1);
    printf(" Time = %10.4f
", t);
    mflops = (double)(2*niter*na) * (3.0 + (double)(NONZER*(NONZER+1))/2.0
        + 2.5*(5.0+(double)(NONZER*(NONZER+1))/2.0) + 2.5) / (t*1000000.0);
    printf(" Mop/s= %10.4f
", mflops);
  }

  return 0;
}
