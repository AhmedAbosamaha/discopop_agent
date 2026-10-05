/* TSVC-2 loop s243, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s243.h"

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

static real_t kernel_s243(void)
{
    // Cache initial values to break cross-iteration dependence on a[i+1]
    real_t *a_init = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        // Refresh the cache with current values of a before the parallel loop
        for (int i = 0; i < LEN_1D; i++) {
            a_init[i] = a[i];
        }

        // Parallel loop: each iteration i reads from a_init[i+1] (constant)
        // and writes only to a[i], b[i], making all iterations independent
        #pragma omp parallel for shared(a, b, c, d, e, a_init)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_init[i+1] * d[i];
        }
        pb_mix(nl);
    }

    free(a_init);
    return (real_t)0;
}

PB_MAIN(kernel_s243)
