/* TSVC-2 loop s1213, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s1213.h"
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

/* The i-loop as written chains iterations in two ways:
 *   a[i] = b[i-1] + c[i]      -- reads b[i-1] just written by iteration i-1
 *   b[i] = a[i+1] * d[i]      -- reads a[i+1], still holding its PRE-sweep
 *                                 value, because iteration i+1 (which would
 *                                 overwrite it) hasn't run yet
 * Substituting the first dependence away shows both new values are in fact
 * functions of only the pre-sweep (old) a[], plus c, d and the untouched
 * b[0]:
 *   b[i]_new = old_a[i+1] * d[i]                           (i = 1 .. LEN_1D-2)
 *   a[1]_new = b[0] + c[1]
 *   a[i]_new = old_a[i] * d[i-1] + c[i]                    (i = 2 .. LEN_1D-2)
 * ( a[i]_new for i>=2 comes from substituting b[i-1]_new = old_a[i]*d[i-1]
 *   into a[i]_new = b[i-1]_new + c[i]. )
 * So taking a snapshot of a[] before the sweep removes the cross-iteration
 * dependence entirely: every iteration of the rewritten loop reads only the
 * snapshot, c, d and b[0] (none of which it or any other iteration writes)
 * and writes only its own a[i]/b[i]. old_a is heap-allocated once (its size
 * tracks LEN_1D, which can be huge) and reused across repetitions. */
static real_t kernel_s1213(void)
{
    real_t *old_a = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        /* Snapshot: old_a[i] = a[i] for every index the i-loop below reads
         * (1 .. LEN_1D-1). Disjoint writes (old_a[i]) from disjoint reads
         * (a[i]) per iteration -- safe to parallelize. */
        #pragma omp parallel for shared(a, old_a) schedule(static)
        for (int i = 1; i < LEN_1D; i++) {
            old_a[i] = a[i];
        }
        /* Each iteration writes only a[i] and b[i], and reads only old_a[i],
         * old_a[i+1], c[i], d[i], d[i-1] and the never-written-here b[0]:
         * no iteration reads anything another iteration of this loop
         * writes, so iterations are independent. */
        #pragma omp parallel for shared(a, b, c, d, old_a) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = old_a[i+1] * d[i];
            a[i] = (i == 1) ? (b[0] + c[1]) : (old_a[i] * d[i-1] + c[i]);
        }
        pb_mix(nl);
    }
    free(old_a);
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
