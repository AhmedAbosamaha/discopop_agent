#include "data.h"
#include "tsvc_c3/s3112.h"

int dummy(real_t *a, real_t *b, real_t *c, real_t *d, real_t *e, real_t s)
{
  static long n = 0;
  long k = (n * 7919L + 13L) % LEN_1D;
  pb_fold(n, a, b, c, d, e, s);
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
  n++;
  return 0;
}

int main(int argc, char** argv)
{
  if (pb_setup(argc, argv)) return 1;
  pb_timer_start();
  real_t pb_result = kernel_s3112();
  pb_timer_stop();
  pb_finish(pb_result);
  return 0;
}
