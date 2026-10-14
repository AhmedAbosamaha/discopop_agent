#include "data.h"
#include "tsvc_c5/s2111.h"

int dummy(real_t *a, real_t *b, real_t *c, real_t *d, real_t *e, real_t (*aa)[LEN_2D], real_t (*bb)[LEN_2D], real_t (*cc)[LEN_2D])
{
  static long n = 0;
  long k = (n * 7919L + 13L) % LEN_1D;
  pb_fold(n, a, b, c, d, e, (real_t)0);
  pb_fold_2d(n, aa, bb, cc);
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
  long p = 1 + (n * 7919L + 13L) % (LEN_2D - 1);
  long q = 1 + (n * 104729L + 7L) % (LEN_2D - 1);
  aa[0][q] += (real_t)0.125; aa[p][0] += (real_t)0.125;
  bb[0][q] += (real_t)0.125; bb[p][0] += (real_t)0.125;
  cc[p][q] += (real_t)0.125;
  n++;
  return 0;
}

int main(int argc, char** argv)
{
  if (pb_setup(argc, argv)) return 1;
  pb_timer_start();
  real_t pb_result = kernel_s2111();
  pb_timer_stop();
  pb_finish(pb_result);
  return 0;
}
