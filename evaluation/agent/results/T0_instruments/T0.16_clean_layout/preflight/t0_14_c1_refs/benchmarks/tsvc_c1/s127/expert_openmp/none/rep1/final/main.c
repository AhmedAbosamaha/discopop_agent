#include "data.h"
#include "tsvc_c1/s127.h"

static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

int main(int argc, char** argv)
{
  if (pb_setup(argc, argv)) return 1;
  pb_timer_start();
  real_t pb_result = (real_t)0;
  for (int nl = 0; nl < R; nl++) {
    pb_result = kernel_s127();
    pb_mix(nl);
  }
  pb_timer_stop();
  pb_finish(pb_result);
  return 0;
}
