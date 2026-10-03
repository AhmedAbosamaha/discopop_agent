/* TSVC-2 loop s322, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s322.h"

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

static real_t kernel_s322(void)
{
    /* Both loops here carry a true (flow) dependence, not a reused location:
     * - nl: pb_mix(nl) rewrites a[0], b[LEN_1D-1] and a/b/c/d/e[k], and those
     *   values are read back by the *entire* recurrence sweep of the next nl,
     *   so repetitions cannot be reordered, split, or run concurrently.
     * - i: a[i] reads a[i-1] and a[i-2], which were WRITTEN by earlier
     *   iterations of this very loop (for i >= 3). This is a genuine order-2
     *   linear recurrence spanning the whole array: every a[i] depends on the
     *   full in-order history back to a[0]/a[1]. It is not an accumulator
     *   (not reducible) and not per-iteration scratch (not privatizable).
     *   Any scheme that lets threads compute disjoint ranges in parallel
     *   (block/scan/cyclic-reduction style techniques) must re-associate the
     *   floating-point multiply-adds into a different grouping than this
     *   serial sweep uses; since +/* are not associative in IEEE 754, that
     *   changes rounding for general b[]/c[]/a[] contents and breaks the
     *   byte-for-byte match against the sequential reference (and the
     *   cross-schedule/cross-thread-count agreement check). A pipelined
     *   construct that preserves the exact sequential arithmetic order adds
     *   only synchronization overhead, since each iteration is 3 FLOPs that
     *   must strictly follow the previous one, so it cannot yield a speedup
     *   either. No #pragma omp is applied to either loop for these reasons. */
    for (int nl = 0; nl < R; nl++) {
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s322)
