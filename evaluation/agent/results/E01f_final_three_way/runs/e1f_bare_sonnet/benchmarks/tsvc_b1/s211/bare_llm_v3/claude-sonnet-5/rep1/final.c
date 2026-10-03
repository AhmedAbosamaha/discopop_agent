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

/* Original loop body:
 *   a[i] = b[i-1] + c[i]*d[i];   // reads the NEW b[i-1], already overwritten this same loop
 *   b[i] = b[i+1] - e[i]*d[i];   // reads the OLD b[i+1], not yet overwritten this loop
 * This is a true dependence carried through the shared array b: iteration i's write to
 * b[i] is read back (as the "new" value) by iteration i+1's computation of a[i+1], while
 * that same statement also needs the "old" (pre-loop) value of b[i+1]. In-place update
 * makes both reads collide on one location visited in two different time-states, which is
 * what blocks parallelizing the fused loop as written.
 *
 * Fix: snapshot b into a heap buffer (oldb) before this repetition's update, so the read
 * of "old b[i+1]" has a location of its own instead of racing the in-place write. Then:
 *   pass 1 (parallel): b[i] = oldb[i+1] - e[i]*d[i]     for i in [1, LEN_1D-2]
 *   pass 2 (parallel): a[i] = b[i-1]    + c[i]*d[i]     for i in [1, LEN_1D-2]
 * Pass 1 only reads oldb (untouched this repetition) and writes distinct b[i] slots: no
 * dependence between its iterations. Pass 2 runs after pass 1 has fully finished (the
 * worksharing loop's implicit barrier), so b[i-1] it reads is exactly the new value the
 * original sequential loop would have produced by the time it reached index i; no
 * dependence between pass 2's iterations either. b[0] is never written by either pass
 * (same as the original, which never updates index 0 in this loop), so pass 2's i==1 read
 * of b[0] still sees the pre-loop value, matching the original execution order exactly.
 * oldb is heap-allocated (malloc/free) because LEN_1D can be far larger than the 8MB stack
 * allows for an automatic array.
 */
static real_t kernel_s211(void)
{
    real_t *oldb = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        /* oldb: heap scratch buffer, written once per index, no cross-iteration reuse. */
        #pragma omp parallel for default(none) shared(oldb, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            oldb[i] = b[i];
        }
        /* b[i] depends only on oldb[i+1], e[i], d[i]: all distinct per iteration. */
        #pragma omp parallel for default(none) shared(oldb, b, e, d) schedule(static)
        for (int i = 1; i < LEN_1D - 1; i++) {
            b[i] = oldb[i + 1] - e[i] * d[i];
        }
        /* a[i] depends only on the now-finalized b[i-1], c[i], d[i]: all distinct per iteration. */
        #pragma omp parallel for default(none) shared(a, b, c, d) schedule(static)
        for (int i = 1; i < LEN_1D - 1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }
        pb_mix(nl);
    }
    free(oldb);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
