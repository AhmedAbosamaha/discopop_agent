/* TSVC-2 loop s292, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s292.h"

/* Between two repetitions a few INPUT elements change, so no repetition can be skipped,
 * merged with another or run out of order: the repetition loop is sequential by a true
 * dependence, and the loop under study is the one inside it. */
static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

static real_t kernel_s292(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* im1/im2 are wrap-around indices: closed form is (i-1, i-2) for i >= 2,
         * (N-1, N-2) for i == 0 and (0, N-1) for i == 1. b is only read. */
        if (LEN_1D > 0)
            a[0] = (b[0] + b[LEN_1D-1] + b[LEN_1D-2]) * (real_t).333;
        if (LEN_1D > 1)
            a[1] = (b[1] + b[0] + b[LEN_1D-1]) * (real_t).333;
        #pragma omp parallel for schedule(static) shared(a, b)
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1] + b[i-2]) * (real_t).333;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s292)
