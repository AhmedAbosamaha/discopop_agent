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
    /* Scratch buffer holding the "new" b values for this repetition, heap-allocated
     * since LEN_1D can be huge; allocated once and reused across all R repetitions
     * so its cost stays O(LEN_1D), not O(R * LEN_1D). */
    real_t *nb = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* b[0] is never written by the loop below (it starts at i=1), so the value
         * a[1] must see for "b[i-1]" at i=1 is simply the current b[0]. */
        nb[0] = b[0];

        /* Each b[i] (for i=1..LEN_1D-2) only ever depends on the pre-repetition value
         * of b[i+1] (that index is untouched until later in program order, so in the
         * original sequential loop it is still old when b[i] is computed). Computing
         * all of these into nb[] first removes that dependence: iterations only read
         * shared, untouched b/d/e and write their own distinct nb[i]. */
        #pragma omp parallel for default(none) shared(b, d, e, nb)
        for (int i = 1; i < LEN_1D-1; i++) {
            nb[i] = b[i + 1] - e[i] * d[i];
        }

        /* a[i] originally read the already-updated b[i-1] from the previous loop
         * iteration; that updated value is exactly nb[i-1] computed above. Since
         * loop A above has fully finished, reading nb[i-1] here is race-free and
         * reproduces the chained value without any cross-iteration dependence.
         * Committing b[i] = nb[i] here finishes the update the original loop made. */
        #pragma omp parallel for default(none) shared(a, b, c, d, nb)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = nb[i - 1] + c[i] * d[i];
            b[i] = nb[i];
        }

        pb_mix(nl);
    }

    free(nb);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
