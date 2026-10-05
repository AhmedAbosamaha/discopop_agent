/* TSVC-2 loop s1213, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s1213.h"
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

static real_t kernel_s1213(void)
{
    /* Heap-allocated scratch: snapshot of a[] as it stood before each
     * repetition's inner loop. Size scales with LEN_1D, so it must not be
     * a stack array. Allocated once and reused across repetitions. */
    real_t *oldA = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* The textual loop reads b[i-1] (the value written one iteration
         * earlier THIS activation) and a[i+1] (the value not yet written
         * this activation, i.e. still the pre-loop value). Expanding the
         * recurrence shows every new value is actually expressible purely
         * from values present at loop entry:
         *   b_new[i] = a_old[i+1] * d[i]                      (all i)
         *   a_new[i] = a_old[i] * d[i-1] + c[i]                (i >= 2)
         *   a_new[1] = b_old[0] + c[1]                         (boundary:
         *              b[0] is never written by this loop)
         * so the iterations become independent once reads go through a
         * snapshot (oldA, b0) taken before this activation instead of the
         * live, concurrently-written arrays a/b. */
        real_t b0 = b[0];

        /* Independent per-element copy: fills oldA, no cross-iteration
         * dependence. a is read-only here (snapshot source), oldA is the
         * write target, disjoint per i. */
        #pragma omp parallel for default(none) shared(a, oldA) schedule(static)
        for (int i = 0; i < LEN_1D; i++)
            oldA[i] = a[i];

        /* Each iteration writes only a[i] and b[i] (disjoint across i) and
         * reads only oldA/c/d (never written by this loop) and the
         * firstprivate scalar b0 captured before the loop. No iteration
         * depends on another any more, so any order/schedule is safe.
         * a, b: shared, written per-i, disjoint -> race-free.
         * c, d, oldA: shared, read-only in this loop.
         * b0: firstprivate -- read-only value computed before the loop,
         *      not needed after it. */
        #pragma omp parallel for default(none) shared(a, b, c, d, oldA) firstprivate(b0) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            if (i == 1)
                a[i] = b0 + c[i];
            else
                a[i] = oldA[i]*d[i-1] + c[i];
            b[i] = oldA[i+1]*d[i];
        }
        pb_mix(nl);
    }
    free(oldA);
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
