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
    /* Heap temp holding the new values of b: b_new[i] depends only on OLD
     * b[i+1], and a[i] depends on b_new[i-1].  Computing b_new into bt first
     * and then a/b from bt removes the loop-carried dependence through b. */
    real_t *bt = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        /* Pass 1: new b values from old b (reads b, e, d; writes only bt). */
#pragma omp parallel for default(none) shared(b, e, d, bt) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            bt[i] = b[i + 1] - e[i] * d[i];
        }
        /* b[0] is never written by the loop, so b_new[0] == b_old[0]. */
        bt[0] = b[0];
        /* Pass 2: a[i] from b_new[i-1], and commit b_new into b. */
#pragma omp parallel for default(none) shared(a, b, c, d, bt) schedule(static)
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
