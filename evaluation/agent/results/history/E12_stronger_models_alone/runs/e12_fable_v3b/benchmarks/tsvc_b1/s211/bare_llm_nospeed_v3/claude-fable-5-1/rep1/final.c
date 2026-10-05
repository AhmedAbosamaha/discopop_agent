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
    /* Temporary holding the new values of b, so that the flow dependence
     * a[i] <- b[i-1] (written by iteration i-1) is carried across two
     * independent loops instead of between iterations of one loop. */
    real_t *bt = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        /* Phase 1: new b values from the ORIGINAL b (b[i+1] is never
         * modified before iteration i reads it in the sequential code). */
#pragma omp parallel for shared(b, d, e, bt)
        for (int i = 1; i < LEN_1D-1; i++) {
            bt[i] = b[i + 1] - e[i] * d[i];
        }
        /* b[0] is never written by the loop; iteration i=1 reads it as is. */
        bt[0] = b[0];
        /* Phase 2: a[i] uses the already-updated b[i-1] (= bt[i-1]),
         * then commit the new b values. */
#pragma omp parallel for shared(a, b, c, d, bt)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = bt[i - 1] + c[i] * d[i];
            b[i] = bt[i];
        }
        pb_mix(nl);
    }
    free(bt);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
