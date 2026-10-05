/* TSVC-2 loop s121, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s121.h"
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

static real_t kernel_s121(void)
{
    /* a[i] = a[i+1] + b[i] has a backward (anti) dependence: a[i+1] is read by
     * iteration i and written by iteration i+1. In the original left-to-right
     * order that read always sees the pre-loop value of a[i+1], so to run the
     * iterations in parallel (any order) we snapshot a[] into a_old[] first and
     * read exclusively from the snapshot, writing only into a[]. That makes
     * every iteration's read and write sets disjoint across iterations. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot: a_old is write-only here (each k written by exactly one
         * iteration), a is read-only here (its contents at loop entry). */
        #pragma omp parallel for schedule(static) shared(a, a_old)
        for (int k = 0; k < LEN_1D; k++) {
            a_old[k] = a[k];
        }

        /* Compute: reads only from the immutable snapshot a_old, writes only
         * to the disjoint index i of a. j is declared inside the loop body,
         * so it is already private per iteration (no clause needed). */
        #pragma omp parallel for schedule(static) shared(a, b, a_old)
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;
            a[i] = a_old[j] + b[i];
        }

        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s121)
