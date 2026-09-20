#include "kern.h"
#include <stdlib.h>
double a[R][T];
double b[R];
void kernel(int n)
{
  int i, t;
  #pragma omp parallel for private(t) shared(a) firstprivate(n)
  for (i = 0; i < n; i++)
    for (t = 1; t < T; t++)
      a[i][t] = a[i][t-1] * 0.5 + 1.0;
}
void smooth(int n)
{
  int m, nb, blk;
  const int BS = 64;
  double *carry;

  if (n <= 1) return;

  m = n - 1; /* last valid index; also the count of elements i=1..m */
  nb = (m + BS - 1) / BS;

  carry = (double *) malloc((size_t)(nb + 1) * sizeof(double));
  carry[0] = b[0];

  /* Phase 1: per-block local recurrence assuming a zero carry-in.
     Each block writes only its own disjoint range of b[], so the
     blocks are independent and safe to run in parallel. */
  #pragma omp parallel for schedule(static) firstprivate(m, nb) shared(a, b)
  for (blk = 0; blk < nb; blk++) {
    int start = 1 + blk * BS;
    int end = start + BS - 1;
    double prev;
    int idx;
    if (end > m) end = m;
    prev = 0.0;
    for (idx = start; idx <= end; idx++) {
      prev = prev * 0.5 + a[idx][T-1];
      b[idx] = prev;
    }
  }

  /* Phase 2: combine the true carry-in across block boundaries.
     This still carries the real dependence, but it only runs nb times
     (one step per block), so it stays sequential and cheap. */
  for (blk = 0; blk < nb; blk++) {
    int start = 1 + blk * BS;
    int end = start + BS - 1;
    int len, k;
    double sc;
    if (end > m) end = m;
    len = end - start + 1;
    sc = 1.0;
    for (k = 0; k < len; k++) sc *= 0.5;
    carry[blk + 1] = sc * carry[blk] + b[end];
  }

  /* Phase 3: apply each block's true carry-in, scaled by the matching
     power of 0.5, to every element of that block. Blocks are disjoint,
     so this is again safe to run in parallel. */
  #pragma omp parallel for schedule(static) firstprivate(m, nb) shared(b, carry)
  for (blk = 0; blk < nb; blk++) {
    int start = 1 + blk * BS;
    int end = start + BS - 1;
    double c, sc;
    int idx;
    if (end > m) end = m;
    c = carry[blk];
    sc = 1.0;
    for (idx = start; idx <= end; idx++) {
      sc *= 0.5;
      b[idx] = b[idx] + sc * c;
    }
  }

  free(carry);
}
