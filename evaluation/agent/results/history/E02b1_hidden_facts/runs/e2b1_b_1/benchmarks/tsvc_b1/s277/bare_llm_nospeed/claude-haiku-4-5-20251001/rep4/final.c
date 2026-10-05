/* TSVC-2 loop s277, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s277.h"
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

static real_t kernel_s277(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Allocate temporary buffer for phase 1 */
        real_t *b_new = (real_t *)malloc(sizeof(real_t) * LEN_1D);
        memcpy(b_new, b, sizeof(real_t) * LEN_1D);

        /* Phase 1: Compute all b[i+1] values in parallel.
         * Each iteration i reads a[i], c[i], d[i], e[i] (invariant between iterations)
         * and writes to b_new[i+1] (unique per iteration, no conflicts).
         * No loop-carried dependence since all reads are from initial state.
         */
        #pragma omp parallel for schedule(static) \
            shared(a, b_new, c, d, e)
        for (int i = 0; i < LEN_1D-1; i++) {
            if (a[i] < (real_t)0.) {
                b_new[i+1] = c[i] + d[i] * e[i];
            }
        }

        /* Phase 2: Update all a[i] values in parallel, using pre-computed b_new values.
         * Each iteration i reads a[i], b_new[i], c[i], d[i] (all from single snapshot after phase 1)
         * and writes to a[i] (unique per iteration, no conflicts).
         * No loop-carried dependence since b_new is finalized from phase 1.
         */
        #pragma omp parallel for schedule(static) \
            shared(a, b_new, c, d)
        for (int i = 0; i < LEN_1D-1; i++) {
            if (a[i] < (real_t)0. && b_new[i] < (real_t)0.) {
                a[i] += c[i] * d[i];
            }
        }

        /* Copy computed b values back to b */
        memcpy(b, b_new, sizeof(real_t) * LEN_1D);
        free(b_new);

        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s277)
