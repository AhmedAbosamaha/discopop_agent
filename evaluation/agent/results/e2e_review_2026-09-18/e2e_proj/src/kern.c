#include "kern.h"
double a[R][T];
double b[R];
void kernel(int n)
{
  int i, t;
  #pragma omp parallel for private(t) firstprivate(n) shared(a)
  for (i = 0; i < n; i++)
    for (t = 1; t < T; t++)
      a[i][t] = a[i][t-1] * 0.5 + 1.0;
}
void smooth(int n)
{
  int i;
  for (i = 1; i < n; i++)
    b[i] = b[i-1] * 0.5 + a[i][T-1];
}
