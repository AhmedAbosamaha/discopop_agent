/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"

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

static real_t kernel_s341(void)
{
    int j;
    for (int nl = 0; nl < R; nl++) {
        j = 0;
        /* Original dependence: j is an exclusive running count of how many
         * earlier i's had b[i] > 0, used as the write slot for a[]. That is
         * an exclusive prefix-sum (scan) of the predicate, not a reused
         * location - the count really has to flow from i-1 into i. We keep
         * the scan order (so results match exactly) but let OpenMP's inscan
         * reduction carry the running count across threads: each iteration
         * reads j as the exclusive prefix before this i (pre-scan part),
         * then folds in its own predicate via the combiner update after the
         * scan directive. pred is loop-local (private by construction); j
         * is never read once this loop ends, so reduction is safe. a[] and
         * b[] stay shared - each iteration writes a distinct a[j] slot and
         * reads a distinct b[i], so there is no race between iterations.
         */
        #pragma omp parallel for reduction(inscan, +:j)
        for (int i = 0; i < LEN_1D; i++) {
            int pred = (b[i] > (real_t)0.) ? 1 : 0;
            if (pred) a[j] = b[i];
            #pragma omp scan exclusive(j)
            j += pred;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s341)
