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
    /* Heap-allocated snapshot of a[] as it stood before this activation of the
     * inner loop. The original code's b[i] = a[i]*a[i+1]*d[i] always reads
     * a[i+1] as it was before the loop started (iteration i runs before the
     * iteration i+1 that would overwrite it), so capturing that snapshot and
     * reading it instead of the live array removes the loop-carried
     * dependence and lets all i run in any order. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* a_old: written once per element, read only after this copy loop
         * completes (in the loop below) -> shared, race-free. a: read-only
         * here. */
        #pragma omp parallel for default(none) shared(a, a_old)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        /* anew is declared inside the loop body: per-iteration scratch, no
         * clause needed. b, c, d, a_old: each i only reads its own b[i],
         * c[i], d[i], a_old[i+1] -> shared, no races. a, b: each i writes
         * only its own a[i], b[i] -> shared, disjoint writes, no races. */
        #pragma omp parallel for default(none) shared(a, b, c, d, a_old)
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t anew = b[i] * c[i] * d[i];
            a[i] = anew;
            b[i] = anew * a_old[i+1] * d[i];
        }
        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s241)
