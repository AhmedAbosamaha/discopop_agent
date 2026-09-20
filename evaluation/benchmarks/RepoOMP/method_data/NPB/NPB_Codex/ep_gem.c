#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <omp.h>
#include "npb-C.h"

#define	MK		16
#define	MM		(M - MK)
#define	NN		(1 << MM)
#define	NK		(1 << MK)
#define	NQ		10
#define EPSILON		1.0e-8
#define	A		1220703125.0
#define	S		271828183.0
#define	TIMERS_ENABLED	FALSE

static double	x[2*NK];
static double	q[NQ];

int main(int argc, char **argv) {

  double	mops, t1, t2, t3, t4, x1, x2, sx, sy, tm, an, tt;
  double	sx_verify, sy_verify, sx_sum, sy_sum;
  int		np;
  int		i, k, nit;
  boolean	verified;
  char		size[13+1];

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

  if (fscanf(fp, "%d", &M) != 1) {
    fprintf(stderr, "error in reading M
");
    exit(1);
  }
  fclose(fp);

  np = NN;

  vranlc(0, &t1, A, x);
  t1 = A;
  for (i = 0; i < 2 * NK; i++)
    x[i] = randlc(&t1, t1);

  an = A;
  t1 = A;
  tt = S;
  sx = 0.0;
  sy = 0.0;

#pragma omp parallel for private(k, x1, x2, i, sx_verify, sy_verify, an, tt) reduction(+:sx, :sy)
  for (k = 1; k <= np; k++) {
    x1 = 2.0 * randlc(&t1, an) - 1.0;
    x2 = 2.0 * randlc(&t1, an) - 1.0;
    t2 = x1*x1 + x2*x2;
    if (t2 <= 1.0) {
      t3 = sqrt(t2);
      t4 = log(t3);
      sx_verify = -2.0 * t4 / t3 * x1;
      sy_verify = -2.0 * t4 / t3 * x2;
      sx = sx + sx_verify;
      sy = sy + sy_verify;
    }
  }
  sx_sum = 0.0;
  sy_sum = 0.0;

  printf("

 NAS Parallel Benchmarks 3.0 structured OpenMP C version - EP Benchmark
");
  printf("
 Size: %12d
", M);
  printf(" Iterations: %5d
", nit);

  verified = FALSE;
  if (M == 24) {
    sx_verify = -3.247834652034740e+3;
    sy_verify = -6.958407078382297e+3;
  } else if (M == 25) {
    sx_verify = -2.863319731645753e+3;
    sy_verify = -6.320053679109499e+3;
  } else if (M == 28) {
    sx_verify = -4.295875165629892e+3;
    sy_verify = -1.580732573675924e+4;
  } else if (M == 30) {
    sx_verify =  4.033815542441498e+4;
    sy_verify = -2.660669192809235e+4;
  } else if (M == 32) {
    sx_verify =  4.764367927995374e+4;
    sy_verify = -8.084072988055743e+4;
  } else if (M == 36) {
    sx_verify =  1.982481200946593e+5;
    sy_verify = -1.020596636367674e+5;
  } else if (M == 40) {
    sx_verify = -5.319717441530e+05;
    sy_verify = -3.726432252152e+05;
  }

  if (verified) {
    printf(" Result verification successful
");
  } else {
    printf(" Result verification failed
");
  }

  mops = pow(2.0, M+1)/tm/1000000.0;

  printf("
 EP Benchmark Results:
");
  printf(" CPU Time = %10.4f
", tm);
  printf(" N = 2^%5d
", M);
  printf(" No. Gaussian Pairs = %15.0f
", (double)np);
  printf(" Sums = %25.15e %25.15e
", sx, sy);
  printf(" Pairwise Sums = %25.15e %25.15e
", sx_sum, sy_sum);
  printf(" Mop/s = %15.2f
", mops);
  printf(" Operation type  = %s
", "floating point");
  printf(" Verification    = %s
", (verified) ? "SUCCESSFUL" : "UNSUCCESSFUL");
  printf(" Version         = %s
", "3.0");
  printf(" Compile date    = %s
", __DATE__);
  printf(" Compile time    = %s
", __TIME__);
  printf(" NPB Class       = %c
", size[0]);


  return 0;
}

