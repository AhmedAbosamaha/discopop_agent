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
    /* Heap-allocated (LEN_1D can be up to 192,000,000): a snapshot of b taken
     * before each repetition's inner loop runs, so that loop's iterations can
     * be computed independently of each other (see rationale below). */
    real_t *b_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot b before it is modified by this repetition's inner loop.
         * Plain array copy, no cross-iteration dependence: b_old[i] <- b[i]. */
        #pragma omp parallel for default(none) shared(b, b_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            b_old[i] = b[i];
        }

        /* Original loop:
         *   a[i] = b[i-1] + c[i]*d[i];      // b[i-1] here is the value b[i-1]
         *                                   // was just overwritten to by the
         *                                   // previous iteration (i-1), i.e. a
         *                                   // true value flowing between
         *                                   // iterations.
         *   b[i] = b[i+1] - e[i]*d[i];      // b[i+1] is still the pre-loop
         *                                   // value here (it is not written
         *                                   // until iteration i+1 runs), so
         *                                   // this part never depended on
         *                                   // other iterations at all.
         *
         * The iteration-(i-1) definition of the new b[i-1] is itself
         *   b[i-1] = b_old[i] - e[i-1]*d[i-1]      (for i-1 >= 1, i.e. i >= 2)
         * and for i == 1, index 0 of b is never written by this loop, so the
         * value a[1] needs is simply b_old[0]. Substituting removes the
         * recurrence: every iteration now reads only the pre-loop snapshot
         * b_old plus c/d/e, and writes only its own a[i]/b[i] -- the same
         * floating-point operations as the original, in the same order, just
         * expressed without the carried value. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, b_old) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            real_t bprev; /* per-iteration scratch, declared inside the loop */
            if (i == 1) {
                bprev = b_old[0];
            } else {
                bprev = b_old[i] - e[i - 1] * d[i - 1];
            }
            a[i] = bprev + c[i] * d[i];
            b[i] = b_old[i + 1] - e[i] * d[i];
        }
        pb_mix(nl);
    }

    free(b_old);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
