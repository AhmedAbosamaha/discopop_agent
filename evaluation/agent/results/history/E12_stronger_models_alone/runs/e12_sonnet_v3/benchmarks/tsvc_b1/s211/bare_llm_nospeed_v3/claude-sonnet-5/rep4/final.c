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
    /* Heap-allocated scratch buffer holding the "new" b[] values for one repetition,
     * sized LEN_1D (which can be up to 192000000 in the verification builds) so it
     * must live on the heap, not the stack. */
    real_t *nb = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* The original loop has, through b[], a true dependence (a[i] reads the b[i-1]
         * already overwritten by iteration i-1, or the untouched b[0] when i==1) and an
         * anti dependence (b[i] reads the b[i+1] that iteration i+1 has not overwritten
         * yet). Both sides are fully determined by the b[] values present before this
         * inner-loop invocation starts: b_new[i] = b_old[i+1] - e[i]*d[i] for every i,
         * independent of execution order. So we (1) compute all new b values into nb[]
         * from the untouched b[] snapshot, (2) compute a[] from nb[] (seeding nb[0] with
         * the old b[0] so i==1 matches the original), (3) publish nb[] back into b[].
         * Each pass is independent across i; the implicit barrier between the three
         * parallel-for regions makes pass 2 see a fully-populated nb[] and keeps pass 3
         * from racing with pass 1's reads of the old b[]. */
        nb[0] = b[0];

        #pragma omp parallel for default(none) shared(b, d, e, nb)
        for (int i = 1; i < LEN_1D - 1; i++) {
            nb[i] = b[i + 1] - e[i] * d[i];
        }

        #pragma omp parallel for default(none) shared(a, c, d, nb)
        for (int i = 1; i < LEN_1D - 1; i++) {
            a[i] = nb[i - 1] + c[i] * d[i];
        }

        #pragma omp parallel for default(none) shared(b, nb)
        for (int i = 1; i < LEN_1D - 1; i++) {
            b[i] = nb[i];
        }

        pb_mix(nl);
    }

    free(nb);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
