#include "kern.h"
double a[R][T];
double b[R];
void kernel(int n)
{
  int i, t;
  #pragma omp parallel for private(t) firstprivate(n)
  for (i = 0; i < n; i++)
    for (t = 1; t < T; t++)
      a[i][t] = a[i][t-1] * 0.5 + 1.0;
}
void smooth(int n)
{
  int i;
  double b0 = b[0];
  #pragma omp parallel for firstprivate(b0)
  for (i = 1; i < n; i++) {
    double val = b0;
    int k;
    for (k = 1; k <= i; k++)
      val = val * 0.5 + a[k][T-1];
    b[i] = val;
  }
}
