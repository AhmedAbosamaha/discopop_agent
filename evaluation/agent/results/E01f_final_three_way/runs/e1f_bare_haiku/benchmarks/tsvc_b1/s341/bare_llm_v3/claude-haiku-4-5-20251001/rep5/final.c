/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"
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

static real_t kernel_s341(void)
{
    int j;
    /* Allocate index array for position mapping: indices[i] stores the output position
     * for b[i] if it is positive, or -1 if b[i] <= 0. */
    int *indices = (int *)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < R; nl++) {
        /* Phase 1 (parallel): Mark which input indices are positive.
         * No inter-iteration dependence: each iteration marks only indices[i]. */
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            indices[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Phase 2 (serial): Compute output positions via prefix sum.
         * This step is inherently sequential (each position depends on all earlier counts),
         * but is O(LEN_1D) and a constant-factor overhead. */
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (indices[i] == 1) {
                indices[i] = count++;
            } else {
                indices[i] = -1;
            }
        }

        /* Phase 3 (parallel): Gather positive elements to output array.
         * Each iteration is independent: iteration i writes to a[indices[i]] if indices[i] >= 0.
         * indices[] is read-only here, and a[indices[i]] writes to disjoint locations for different i. */
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            if (indices[i] >= 0) {
                a[indices[i]] = b[i];
            }
        }

        pb_mix(nl);
    }

    free(indices);
    return (real_t)0;
}

PB_MAIN(kernel_s341)
