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
    real_t *b_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Parallel loop: compute new b values in temporary buffer.
         * No loop-carried dependence: iteration i reads b[i+1] (input),
         * writes b_new[i]; iteration i+1 reads b[i+2], writes b_new[i+1]. */
        #pragma omp parallel for shared(b, b_new, e, d)
        for (int i = 1; i < LEN_1D-1; i++) {
            b_new[i] = b[i + 1] - e[i] * d[i];
        }

        /* Copy new b values back to b. */
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_new[i];
        }

        /* Parallel loop: compute a values using updated b.
         * No loop-carried dependence: iteration i reads b[i-1], c[i], d[i];
         * writes a[i]. Iteration i+1 writes a[i+1], no data dependency. */
        #pragma omp parallel for shared(a, b, c, d)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }

        pb_mix(nl);
    }

    free(b_new);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
