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
    /* im1/im2 in the original sequential version are just (i-1) mod LEN_1D and
     * (i-2) mod LEN_1D, carried forward from iteration to iteration instead of
     * computed from i. That carried state is the only thing stopping the i
     * loop from running in any order: each iteration only ever writes a[i]
     * and reads b[], so recomputing im1/im2 directly from i removes the
     * dependence entirely and lets the loop be parallelized over i. im1/im2
     * are declared inside the loop body, so they are already per-iteration
     * (no data-sharing clause needed); a[] is written once per i (no overlap
     * between iterations) and b[] is only read, so both can be shared.
     */
    for (int nl = 0; nl < R; nl++) {
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
