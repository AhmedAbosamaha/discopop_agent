/* TSVC-2 loop s161, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s161.h"
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

static real_t kernel_s161(void)
{
    /* a_old/c_old: heap snapshots of a[] and c[] taken before each inner-loop
     * pass. The inner loop is the only thing that writes a[] or c[] within a
     * pass (pb_mix runs strictly between passes), and the branch that writes
     * c[i+1] never writes a[i] in the same iteration, so the pre-pass values
     * are exactly what the original sequential execution would have read at
     * index i (and i-1) before any iteration of this pass touched them.
     * Reused across all R repetitions -> O(LEN_1D) extra space, not O(R*LEN_1D). */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *c_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        for (int i = 0; i < LEN_1D; ++i) {
            a_old[i] = a[i];
            c_old[i] = c[i];
        }

        /* The only loop-carried dependence in the original code is: iteration i-1
         * (when b[i-1]<0) overwrites c[i] before iteration i reads it in the
         * "else" branch. That overwritten value is a_old[i-1] + d[i-1]*d[i-1],
         * computable from the pre-pass snapshot alone, so every iteration's
         * effective c[i] can be derived without relying on execution order.
         * Each iteration then writes exactly one of a[i] or c[i+1] -- disjoint
         * locations across i and across the two arrays -- so iterations are
         * independent given the snapshots.
         * Data sharing: a, b, c, d, e, a_old, c_old are the whole-array buffers,
         * shared and either read-only (b, d, e, a_old, c_old) or written at a
         * per-iteration-disjoint index (a, c); i and ci are per-iteration scratch
         * (i is the loop variable, ci is declared inside the loop body). */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, a_old, c_old) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a_old[i] + d[i] * d[i];
            } else {
                real_t ci = (i > 0 && b[i-1] < (real_t)0.)
                                ? (a_old[i-1] + d[i-1] * d[i-1])
                                : c_old[i];
                a[i] = ci + d[i] * e[i];
            }
        }
        pb_mix(nl);
    }

    free(a_old);
    free(c_old);
    return (real_t)0;
}

PB_MAIN(kernel_s161)
