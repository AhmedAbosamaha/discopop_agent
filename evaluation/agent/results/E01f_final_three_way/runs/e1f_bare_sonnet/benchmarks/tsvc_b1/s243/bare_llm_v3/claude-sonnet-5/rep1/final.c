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
    /* a_prev holds a snapshot of a[] taken before this repetition's inner
     * loop writes anything, so the lookahead read of a[i+1] below always
     * sees the same value it would have seen in the original in-order
     * execution (where iteration i+1 has not yet run when iteration i
     * reads a[i+1]). Heap-allocated because LEN_1D can be huge. */
    real_t *a_prev = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot: read-only copy of the pre-iteration a[] values.
         * a is shared (read-only here), a_prev is shared (each iteration
         * writes a distinct index i, so no race). */
        #pragma omp parallel for default(none) shared(a, a_prev)
        for (int i = 0; i < LEN_1D; i++) {
            a_prev[i] = a[i];
        }

        /* Each iteration writes only a[i] and b[i] (distinct per i), and
         * reads c[i], d[i], e[i] (own index only) plus a_prev[i+1], the
         * immutable pre-loop snapshot -- so iterations are independent of
         * each other and may run in any order/schedule/thread count.
         * a, b, c, d, e, a_prev are all shared; i is the loop variable
         * (private by construction). */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, a_prev)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_prev[i+1] * d[i];
        }
        pb_mix(nl);
    }

    free(a_prev);
    return (real_t)0;
}

PB_MAIN(kernel_s243)
