/* TSVC-2 loop s212, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s212.h"
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

static real_t kernel_s212(void)
{
    /* a_orig holds the pre-iteration snapshot of a[] for one repetition. In the original
     * sequential loop, iteration i reads a[i+1] *before* iteration i+1 has a chance to
     * overwrite it (since i+1 runs strictly after i), so b[i] always combines with the
     * value a[i+1] had at loop entry, not any updated value. Copying a[] into a_orig up
     * front turns that "written by an earlier iteration, must not be overtaken" dependence
     * into two independent reads (a_orig[i], a_orig[i+1]) and two independent writes
     * (a[i], b[i]), with no index touched by more than one iteration. a_orig is heap
     * allocated since LEN_1D can be far larger than the stack allows.
     */
    real_t *a_orig = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* Snapshot a[] as it stands at the start of this repetition. a_orig is shared
         * but each iteration writes a distinct index, so there is no overlap between
         * iterations; a is shared and only read here.
         */
        #pragma omp parallel for shared(a, a_orig) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a_orig[i] = a[i];
        }

        /* Independent per-i update: both reads (a_orig[i], a_orig[i+1]) come from the
         * snapshot taken above, and both writes (a[i], b[i]) touch an index that no other
         * iteration writes, so iterations no longer depend on each other's order. a, b, c,
         * d, a_orig are shared arrays; each iteration only accesses its own index i (and
         * i+1 of the read-only snapshot).
         */
        #pragma omp parallel for shared(a, b, c, d, a_orig) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_orig[i] * c[i];
            b[i] += a_orig[i + 1] * d[i];
        }

        pb_mix(nl);
    }

    free(a_orig);
    return (real_t)0;
}

PB_MAIN(kernel_s212)
