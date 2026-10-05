/* TSVC-2 loop s211, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include <stdlib.h>
#include "tsvc_b1/s211.h"

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
    /* Snapshot of b taken before each i-loop runs. a[i] and the new b[i] both need
     * "b as it stood at the start of this repetition", not whatever value some other
     * iteration happens to have already written under a parallel schedule. Using the
     * snapshot for every read turns the sequential recurrence into independent work:
     *   bnew[i]      = bsnap[i+1] - e[i]*d[i]                         (i = 1..LEN_1D-2)
     *   a[1]         = bsnap[0]   + c[1]*d[1]
     *   a[i], i>=2   = bsnap[i] - e[i-1]*d[i-1] + c[i]*d[i]
     * which are exactly the values the original sequential loop computes, re-derived
     * from the pre-loop state instead of from each other. Heap-allocated since LEN_1D
     * can be far larger than the stack allows. */
    real_t *bsnap = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* bsnap: written here (one element per i, disjoint indices); b: read-only here.
         * Plain independent copy, race-free regardless of iteration order. */
        #pragma omp parallel for schedule(static) shared(bsnap, b)
        for (int i = 0; i < LEN_1D; i++) {
            bsnap[i] = b[i];
        }

        /* bsnap, c, d, e: read-only. a, b: each index written by exactly one iteration,
         * using only bsnap/c/d/e values, so no iteration depends on another iteration's
         * write. bi_prev is scratch declared inside the loop body -> private by nature,
         * so it carries no data-sharing clause. */
        #pragma omp parallel for schedule(static) shared(a, b, c, d, e, bsnap)
        for (int i = 1; i < LEN_1D-1; i++) {
            real_t bi_prev;
            if (i == 1) {
                bi_prev = bsnap[0];
            } else {
                bi_prev = bsnap[i] - e[i - 1] * d[i - 1];
            }
            a[i] = bi_prev + c[i] * d[i];
            b[i] = bsnap[i + 1] - e[i] * d[i];
        }

        pb_mix(nl);
    }

    free(bsnap);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
