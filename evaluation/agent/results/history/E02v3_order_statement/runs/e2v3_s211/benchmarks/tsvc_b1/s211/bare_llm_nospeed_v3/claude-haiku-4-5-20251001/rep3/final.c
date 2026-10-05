/* TSVC-2 loop s211, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
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
    /* Allocate temporary buffer for b updates to eliminate loop-carried dependencies */
    real_t *b_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Initialize boundary value for b_new[0] */
        b_new[0] = b[0];

        /* First loop: compute all new b values independently.
         * Each iteration i computes b_new[i] = b[i+1] - e[i]*d[i].
         * No loop-carried dependencies: each iteration reads b[i+1] (not written in this loop)
         * and writes to a distinct b_new[i].
         */
        #pragma omp parallel for private(i) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b_new[i] = b[i + 1] - e[i] * d[i];
        }

        /* Second loop: compute all a values using precomputed b_new values.
         * Each iteration i computes a[i] = b_new[i-1] + c[i]*d[i].
         * No loop-carried dependencies: each iteration reads b_new[i-1] (computed before this loop)
         * and writes to distinct a[i].
         * Semantics preserved: a[i] now uses b_new[i-1] which equals the value b[i-1]
         * would have after iteration i-1 in the original sequential algorithm.
         */
        #pragma omp parallel for private(i) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b_new[i - 1] + c[i] * d[i];
        }

        /* Third loop: update b array with precomputed values.
         * Each iteration i copies b[i] = b_new[i].
         * No loop-carried dependencies: each iteration writes to distinct b[i].
         */
        #pragma omp parallel for private(i) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_new[i];
        }

        pb_mix(nl);
    }

    free(b_new);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
