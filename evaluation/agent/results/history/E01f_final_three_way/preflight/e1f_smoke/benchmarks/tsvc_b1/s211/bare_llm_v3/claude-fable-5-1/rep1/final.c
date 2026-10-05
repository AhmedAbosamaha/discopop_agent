/* TSVC-2 loop s211, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s211.h"
#include <stdlib.h>

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

static real_t kernel_s211(void)
{
    /* bn[i] holds the NEW value of b[i] (for 1 <= i <= LEN_1D-2); bn[0] = b[0],
       which the original loop never writes.  Heap-allocated: size grows with LEN_1D. */
    real_t *bn = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    const int n1 = LEN_1D - 1;

    for (int nl = 0; nl < R; nl++) {
        /* Pass 1: new b values from the OLD b (original anti-dependence on b[i+1]). */
#pragma omp parallel for shared(b, d, e, bn, n1)
        for (int i = 1; i < n1; i++) {
            bn[i] = b[i + 1] - e[i] * d[i];
        }
        bn[0] = b[0];
        /* Pass 2: a[i] uses the new b[i-1] (original flow dependence), then commit b. */
#pragma omp parallel for shared(a, b, c, d, bn, n1)
        for (int i = 1; i < n1; i++) {
            a[i] = bn[i - 1] + c[i] * d[i];
            b[i] = bn[i];
        }
        pb_mix(nl);
    }
    free(bn);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
