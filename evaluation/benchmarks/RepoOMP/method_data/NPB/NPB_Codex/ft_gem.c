#include "npb-C.h"
#include "global.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

#define NU (1+2*NS)
#define NXP (NX+1)
#define NYP (NY+1)

static void cffts1(int,int,int,int,void*,dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX]);
static void cffts2(int,int,int,int,void*,dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX]);
static void cffts3(int,int,int,int,void*,dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX]);
static void checksum(int,dcomplex[NZ][NY][NX],double[2]);
static void cfftz(int,int,int,dcomplex[],dcomplex[]);
static void evolve(dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX],double[NTOTAL]);
static void fft(int,void*,void*);
static void fft_init(int);
static int ilog2(int);
static void init_ui(dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX],dcomplex[NZ][NY][NX]);
static void ipow46(double,int,double*);
static void print_timers(void);
static void setup(int*);
static void verify(int,int,char*,boolean*);

int main(int argc, char **argv) {

  int i;
  int niter;
  char class;
  boolean verified;

  setup(&niter);

  init_ui(u0, u1, u2);

  fft_init(MAXDIM);

  fft(1, u1, u0);

  for (i = 1; i <= niter; i++) {
    evolve(u0, u1, twiddle);
    fft(-1, u1, u2);
    checksum(i, u2, sums);
  }

  verify(NX, NY, &class, &verified);

  if(timeron) print_timers();

  return 0;
}

static void cffts1(
  int is,
  int d1, int d2, int d3,
  void* pointer,
  dcomplex x[d3][d2][d1],
  dcomplex xout[d3][d2][d1],
  dcomplex y[d3][d2][d1])
{
  int i, j, k;
  int logd1;

  logd1 = ilog2(d1);

#pragma omp parallel for private(j, k)
  for (k = 0; k < d3; k++) {
    for (j = 0; j < d2; j++) {
      cfftz(is, logd1, d1, &x[k][j][0], &y[k][j][0]);
    }
  }
}

static void cffts2(
  int is,
  int d1, int d2, int d3,
  void* pointer,
  dcomplex x[d3][d2][d1],
  dcomplex xout[d3][d2][d1],
  dcomplex y[d3][d2][d1])
{
  int i, j, k;
  int logd2;

  logd2 = ilog2(d2);

#pragma omp parallel for private(j, k)
  for (k = 0; k < d3; k++) {
    for (j = 0; j < d2; j++) {
      cfftz(is, logd2, d2, &x[k][j][0], &y[k][j][0]);
    }
  }
}

static void cffts3(
  int is,
  int d1, int d2, int d3,
  void* pointer,
  dcomplex x[d3][d2][d1],
  dcomplex xout[d3][d2][d1],
  dcomplex y[d3][d2][d1])
{
  int i, j, k;
  int logd3;

  logd3 = ilog2(d3);

#pragma omp parallel for private(j, k)
  for (j = 0; j < d2; j++) {
    for (k = 0; k < d3; k++) {
      cfftz(is, logd3, d3, &x[k][j][0], &y[k][j][0]);
    }
  }
}

static void checksum(int i, dcomplex u2[NZ][NY][NX], double sums[2]) {
}

static void cfftz(int is, int m, int n, dcomplex x[], dcomplex y[]) {
}

static void evolve(
  dcomplex u0[NZ][NY][NX],
  dcomplex u1[NZ][NY][NX],
  double twiddle[NTOTAL])
{
  int i, j, k;

#pragma omp parallel for private(i, j, k)
  for (k = 0; k < NZ; k++) {
    for (j = 0; j < NY; j++) {
      for (i = 0; i < NX; i++) {
        u0[k][j][i] = dcmplx_mul(u0[k][j][i], twiddle[k*NY*NX+j*NX+i]);
        u1[k][j][i] = u0[k][j][i];
      }
    }
  }
}

static void fft(int dir, void* x1, void* x2) {
}

static void fft_init(int n) {
}

static int ilog2(int n) {
  return (int)(log((double)n)/log(2.0)+0.5);
}

static void init_ui(
  dcomplex u0[NZ][NY][NX],
  dcomplex u1[NZ][NY][NX],
  dcomplex u2[NZ][NY][NX])
{
}

static void ipow46(double a, int n, double* r) {
}

static void print_timers() {
}

static void setup(int* niter_p) {
}

static void verify(int d1, int d2, char* class, boolean* verified) {
}

