/* TSVC-2 loop s255, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s255.h"

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

static real_t kernel_s255(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Original recurrence: x == b[i-1], y == b[i-2] (indices wrapping around
         * LEN_1D for i==0,1, seeded from b[LEN_1D-1]/b[LEN_1D-2]). Since b[] is
         * only read here (it is mutated by pb_mix() after this loop finishes),
         * x and y can be recovered directly from b[] by index instead of being
         * carried from the previous iteration, making iterations independent. */
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            long im1 = (i == 0) ? (long)LEN_1D - 1 : (long)i - 1;
            long im2 = (i == 0) ? (long)LEN_1D - 2 :
                       (i == 1) ? (long)LEN_1D - 1 : (long)i - 2;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s255)
