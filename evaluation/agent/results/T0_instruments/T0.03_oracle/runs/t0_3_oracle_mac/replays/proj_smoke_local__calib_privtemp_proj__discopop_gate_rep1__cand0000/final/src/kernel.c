#include "bench.h"

double a[N];
double c[N];

void kernel_privtemp(double* a, double* c)
{
  int r, i;
  double t;
  #pragma omp parallel for private(t,i) shared(a,c) 
  for (r = 0; r < R; r++)
    for (i = 0; i < N; i++) {
      t = a[i] * a[i] + 1.0;
      c[i] = t * 0.5 + sqrt(t);
    }
}
