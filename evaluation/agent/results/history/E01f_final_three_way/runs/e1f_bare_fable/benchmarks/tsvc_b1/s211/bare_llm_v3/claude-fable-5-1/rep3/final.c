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
    /* Snapshot of b taken before each repetition: the original loop reads the OLD
     * b[i+1] (anti-dependence) and the NEW b[i-1] (true dependence); with the old
     * values in bt, iteration i can produce both b[i] and a[i+1] independently. */
    real_t *bt = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    const int n = LEN_1D;

    for (int nl = 0; nl < R; nl++) {
        if (n >= 3) {
#pragma omp parallel for default(none) shared(b, bt, n) schedule(static)
            for (int i = 0; i < n; i++) {
                bt[i] = b[i];
            }

            /* i = 1 of the original: b[0] is never written. */
            a[1] = bt[0] + c[1] * d[1];

            /* Original iteration i computes new b[i]; original iteration i+1 then
             * computes a[i+1] = (new b[i]) + c[i+1]*d[i+1].  Same two operations,
             * same order, now in one independent iteration. */
#pragma omp parallel for default(none) shared(a, b, bt, c, d, e, n) schedule(static)
            for (int i = 1; i < n - 2; i++) {
                real_t bn = bt[i + 1] - e[i] * d[i];
                b[i] = bn;
                a[i + 1] = bn + c[i + 1] * d[i + 1];
            }

            /* Last original iteration i = n-2: its new b[n-2] feeds no a[]. */
            b[n - 2] = bt[n - 1] - e[n - 2] * d[n - 2];
        }
        pb_mix(nl);
    }
    free(bt);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
