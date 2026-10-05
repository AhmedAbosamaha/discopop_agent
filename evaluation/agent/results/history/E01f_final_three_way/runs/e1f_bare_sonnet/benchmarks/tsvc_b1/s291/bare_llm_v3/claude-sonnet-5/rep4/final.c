/* TSVC-2 loop s291, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s291.h"

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

static real_t kernel_s291(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* im1 was just "the previous i", wrapping to LEN_1D-1 at i==0; that value
         * is a deterministic function of i alone, so each iteration recomputes it
         * locally instead of carrying it forward. b is only read here (pb_mix
         * mutates it afterwards), and each iteration writes a distinct a[i], so
         * the iterations are independent once im1 is local. */
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? LEN_1D - 1 : i - 1;
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s291)
