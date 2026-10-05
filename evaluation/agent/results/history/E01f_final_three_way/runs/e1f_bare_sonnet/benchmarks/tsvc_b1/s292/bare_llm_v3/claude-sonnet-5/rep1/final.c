/* TSVC-2 loop s292, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s292.h"

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

static real_t kernel_s292(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* im1/im2 only ever held the previous iteration's index value (i-1, i-2,
         * wrapping at the array ends), never a data value carried forward, so they
         * are recomputed here from i directly. Declaring them inside the loop body
         * makes each a fresh per-iteration local -- no data-sharing clause needed --
         * and removes the loop-carried dependence that blocked parallelizing this
         * loop. a[i] is written once per distinct i and b is only read here (it is
         * not mutated until pb_mix runs, after the whole inner loop has finished),
         * so iterations are now fully independent; a and b stay shared (default).
         */
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i - 1 + LEN_1D) % LEN_1D;
            int im2 = (i - 2 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s292)
