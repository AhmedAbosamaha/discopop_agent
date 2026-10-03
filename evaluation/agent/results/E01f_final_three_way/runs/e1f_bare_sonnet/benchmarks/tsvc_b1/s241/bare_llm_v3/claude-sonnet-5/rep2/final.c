/* TSVC-2 loop s241, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s241.h"
#include <stdlib.h>
#include <string.h>

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
    /* a_old holds a snapshot of a[] taken before this repetition's inner loop
     * starts touching it. In the original sequential order, iteration i always
     * ran before iteration i+1, so the a[i+1] read inside b[i]'s formula always
     * saw the pre-repetition value of a[i+1], never a value some other
     * iteration of this same inner loop had just written. Reading from this
     * read-only snapshot instead of the live, concurrently-written a[] removes
     * that loop-carried anti-dependence, so iterations can run in any order
     * (or in parallel) and still reproduce the original values. Heap-allocated
     * because LEN_1D can be very large. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));
        /* a_old: read-only snapshot, shared, indexed per-iteration -> no clause needed beyond shared.
         * b, c, d: shared arrays, each iteration reads/writes only its own index i -> race free.
         * a: shared, each iteration writes only a[i] (distinct per iteration) -> race free.
         * i: loop variable, private by default under omp for. */
        #pragma omp parallel for schedule(static) shared(a, b, c, d, a_old)
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t new_ai = b[i] * c[i  ] * d[i];
            a[i] = new_ai;
            b[i] = new_ai * a_old[i+1] * d[i];
        }
        pb_mix(nl);
    }
    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s241)
