#include "bench.h"

double a[N];
double c[N];

void kernel_privtemp(double* a, double* c)
{
  int r, i;
  double t;
  for (r = 0; r < R; r++)
    #pragma omp parallel for private(t) shared(a,c) 
    for (i = 0; i < N; i++) {
      t = a[i] * a[i] + 1.0;
      c[i] = t * 0.5 + sqrt(t);
    }
}
