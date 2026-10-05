/* TSVC-2 loop s321, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s321.h"
#include <stdlib.h>
#include <string.h>

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

static real_t kernel_s321(void)
{
    const long n = (long)LEN_1D;
    const long nbmax = 256;                 /* at most this many blocks */
    long cs = (n - 1 + nbmax - 1) / nbmax;  /* block size */
    if (cs < 1) cs = 1;
    const long nb = (n > 1) ? (n - 1 + cs - 1) / cs : 0;   /* number of blocks */

    real_t *aold = (real_t *)malloc(sizeof(real_t) * (size_t)n);
    real_t *g    = (real_t *)malloc(sizeof(real_t) * (size_t)(nb > 0 ? nb : 1));

    for (int nl = 0; nl < R; nl++) {
        /* Pre-loop value of each block's predecessor element (speculative start). */
        for (long j = 0; j < nb; j++) {
            g[j] = a[1 + j * cs - 1];
        }

        /* Phase 1: every block runs the recurrence from its guessed start value.
         * Blocks write disjoint ranges of a[] and aold[]; b[] and g[] are read-only. */
        #pragma omp parallel for schedule(static) shared(a, b, aold, g, n, nb, cs)
        for (long j = 0; j < nb; j++) {
            long lo = 1 + j * cs;
            long hi = lo + cs;
            if (hi > n) hi = n;
            real_t x = g[j];
            for (long i = lo; i < hi; i++) {
                real_t old = a[i];
                aold[i] = old;
                x = old + x * b[i];
                a[i] = x;
            }
        }

        /* Phase 2 (serial): propagate the true start value through each block.
         * Block 0 started from a[0], which is never written, so it is already exact.
         * Once a recomputed value is bitwise identical to the speculative one, the
         * rest of the block is unchanged and the walk stops. */
        for (long j = 1; j < nb; j++) {
            long lo = 1 + j * cs;
            long hi = lo + cs;
            if (hi > n) hi = n;
            real_t x = a[lo - 1];
            if (memcmp(&x, &g[j], sizeof(real_t)) == 0) continue;
            for (long i = lo; i < hi; i++) {
                real_t v = aold[i] + x * b[i];
                if (memcmp(&v, &a[i], sizeof(real_t)) == 0) break;
                a[i] = v;
                x = v;
            }
        }
        pb_mix(nl);
    }

    free(aold);
    free(g);
    return (real_t)0;
}

PB_MAIN(kernel_s321)
