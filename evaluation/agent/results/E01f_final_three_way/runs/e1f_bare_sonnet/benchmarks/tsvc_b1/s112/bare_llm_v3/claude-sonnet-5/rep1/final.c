/* TSVC-2 loop s112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s112.h"
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

static real_t kernel_s112(void)
{
    /* Snapshot buffer: holds the pre-repetition values of a[0..LEN_1D-2] so that
     * the shift-and-add below can run with iterations in any order and still see
     * exactly what the original backward loop saw (each a[i] read before the
     * later iteration that would overwrite it). Size scales with LEN_1D, so it
     * is heap-allocated once, reused across the R repetitions, and freed below. */
    real_t *a_old = (real_t *)malloc((size_t)(LEN_1D - 1) * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Read-phase: copy old a[] values out before any of them get overwritten.
         * a_old is written here (disjoint index per iteration, shared, no race);
         * a is read-only shared in this loop. */
        #pragma omp parallel for default(none) shared(a, a_old) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a_old[i] = a[i];
        }

        /* Write-phase: every iteration reads only from the untouched snapshot
         * a_old and b, and writes a distinct element a[i+1], so iterations are
         * now independent of each other and of execution order. a_old and b are
         * read-only shared; a is shared and written at disjoint indices. */
        #pragma omp parallel for default(none) shared(a, a_old, b) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = a_old[i] + b[i];
        }

        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s112)
