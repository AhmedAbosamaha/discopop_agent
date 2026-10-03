/* TSVC-2 loop s254, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s254.h"

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

static real_t kernel_s254(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Original recurrence: x holds b[i-1] (b[LEN_1D-1] when i==0) carried
         * from the previous iteration. Since b is only read here, that value
         * can be fetched directly as b[im1], removing the carried dependence
         * and making each iteration independent. a[i] is written once per i,
         * b is read-only, so iterations may run in any order/thread. */
        #pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            long im1 = (i == 0) ? (long)LEN_1D - 1 : (long)i - 1;
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s254)
