/* TSVC-2 loop s241, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s241.h"
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

static real_t kernel_s241(void)
{
    /* a_old holds the values a[] had before this repetition's i-loop starts.
     * The original loop, run in increasing i order, reads a[i+1] before that
     * slot is ever written in the same pass (iteration i+1 runs later), so
     * b[i] always sees the pre-loop value of a[i+1]. Saving that value up
     * front in a_old lets every i run independently: the true dependence
     * (a[i+1]'s pre-loop value flowing into b[i]) is preserved through the
     * explicit snapshot instead of through execution order. Heap-allocated
     * since LEN_1D can be very large. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot a[] as it stands before this repetition's updates.
         * a, a_old: shared, each iteration i touches only its own index i. */
        #pragma omp parallel for shared(a, a_old)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        /* Independent per i: a[i] depends only on b[i],c[i],d[i]; b[i] uses
         * the just-written a[i] (same iteration) and the pre-loop a[i+1]
         * value captured in a_old, so no iteration depends on another.
         * a, b, c, d, a_old: shared, disjoint per-index reads/writes. */
        #pragma omp parallel for shared(a, b, c, d, a_old)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a_old[i+1] * d[i];
        }
        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s241)
