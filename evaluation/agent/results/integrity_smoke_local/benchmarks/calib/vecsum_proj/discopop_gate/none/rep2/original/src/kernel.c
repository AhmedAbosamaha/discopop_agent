#include "bench.h"

double a[N];
double b[N];
double c[N];

void kernel_vecsum(double* a, double* b, double* c)
{
  int r, i;
  for (r = 0; r < R; r++)
    for (i = 0; i < N; i++)
      c[i] = 0.5 * c[i] + a[i] * b[i] + 0.5 * a[i];
}
