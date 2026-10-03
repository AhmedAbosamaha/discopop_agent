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
        /* Peeled i = 0 and i = 1: these use the wrapped-around seeds
         * x = b[LEN_1D-1], y = b[LEN_1D-2]. */
        a[0] = (b[0] + b[LEN_1D-1] + b[LEN_1D-2]) * (real_t).333;
        a[1] = (b[1] + b[0] + b[LEN_1D-1]) * (real_t).333;
        /* For i >= 2 the carried scalars are exactly x = b[i-1], y = b[i-2]. */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 2; i < LEN_1D; i++) {
            real_t x = b[i-1];
            real_t y = b[i-2];
            a[i] = (b[i] + x + y) * (real_t).333;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s255)
