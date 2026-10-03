/* TSVC-2 loop s243, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s243.h"
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

static real_t kernel_s243(void)
{
    /* Snapshot of a[] taken before each i-loop repetition, used only to supply
     * the a[i+1] value the original sequential order would have read (the
     * value as it stood before this repetition's i-loop started touching it).
     * Heap-allocated because LEN_1D can be far larger than the stack allows. */
    real_t *aold = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* aold: shared, written once per index by its own iteration (disjoint
         * writes) from a (shared, read-only here) -- plain elementwise copy. */
        #pragma omp parallel for shared(a, aold)
        for (int i = 0; i < LEN_1D; i++) {
            aold[i] = a[i];
        }

        /* Each iteration i writes only a[i] and b[i] (disjoint across i), and
         * reads c[i], d[i], e[i] (never written by this loop) plus aold[i+1]
         * (the frozen pre-repetition snapshot, never written by this loop).
         * That removes the anti-dependence that a[i+1] carried in the
         * original code, making iterations independent of each other and of
         * their execution order. a, b, c, d, e, aold: shared. */
        #pragma omp parallel for shared(a, b, c, d, e, aold)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + aold[i+1] * d[i];
        }
        pb_mix(nl);
    }

    free(aold);
    return (real_t)0;
}

PB_MAIN(kernel_s243)
