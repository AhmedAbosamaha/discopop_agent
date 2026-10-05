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
        /* Original form threaded x = b[i-1], y = b[i-2] through the loop, but both
         * are just b read one and two slots behind the current index, wrapping
         * around at the ends (initialised from b[LEN_1D-1]/b[LEN_1D-2]). Reading
         * b directly at the wrapped-around indices removes the loop-carried
         * dependence entirely: every iteration only reads b (unmodified during
         * this inner loop) and writes its own a[i], so iterations are independent. */
        #pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i - 1 + LEN_1D) % LEN_1D;
            int im2 = (i - 2 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s255)
