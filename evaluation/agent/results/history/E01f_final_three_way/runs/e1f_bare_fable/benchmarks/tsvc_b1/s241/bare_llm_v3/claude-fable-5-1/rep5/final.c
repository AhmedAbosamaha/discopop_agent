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
    /* Heap scratch for the new values of a: writing them here instead of into a[]
     * removes the anti-dependence on a[i+1] (iteration i must read the OLD a[i+1]). */
    real_t *a_new = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    if (a_new == NULL) return (real_t)0;

    for (int nl = 0; nl < R; nl++) {
        /* Phase 1: every iteration reads only old a[], b[], c[], d[] and writes
         * a_new[i] and b[i] -- fully independent. */
#pragma omp parallel for shared(a, b, c, d, a_new) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a_new[i] = b[i] * c[i  ] * d[i];
            b[i]     = a_new[i] * a[i+1] * d[i];
        }
        /* Phase 2: commit the new a values once nobody needs the old ones. */
#pragma omp parallel for shared(a, a_new) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_new[i];
        }
        pb_mix(nl);
    }
    free(a_new);
    return (real_t)0;
}

PB_MAIN(kernel_s241)
