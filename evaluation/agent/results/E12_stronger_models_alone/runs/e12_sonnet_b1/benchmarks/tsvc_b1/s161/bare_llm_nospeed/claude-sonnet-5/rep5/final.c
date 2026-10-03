/* TSVC-2 loop s161, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s161.h"
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

/* Inner-loop dependence analysis (per repetition nl):
 * b, d, e are only read in the inner loop, never written -> safe to read live.
 * a and c are each written by at most one disjoint index per iteration
 * (a[i] when b[i]>=0, c[i+1] when b[i]<0), so writes never collide.
 * The only cross-iteration hazard is the else-branch read of c[i], which in
 * sequential order may have just been set by iteration i-1 (when b[i-1]<0,
 * writing c[i] = a[i-1] + d[i-1]^2, using the PRE-LOOP a[i-1] since that
 * branch never touches a[i-1]). Because b is unmodified during this inner
 * loop, that one-hop lookback is fully determined before the loop runs, so
 * we snapshot a and c as they stood at loop entry (a_snap, c_snap) and let
 * every iteration compute its effective c[i] from the snapshot instead of
 * from a live, possibly concurrently-written, array. */
static real_t kernel_s161(void)
{
    real_t *a_snap = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    real_t *c_snap = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        memcpy(a_snap, a, sizeof(real_t) * (size_t)LEN_1D);
        memcpy(c_snap, c, sizeof(real_t) * (size_t)LEN_1D);

        /* a, b, c, d, e: shared arrays. a and c are each written at a single
         * index per iteration, disjoint across iterations; all reads needed
         * across iterations come from the read-only snapshots a_snap/c_snap
         * (or from b/d/e, which this loop never writes). c_eff is declared
         * inside the loop body, so it is already private per iteration. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, a_snap, c_snap) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a_snap[i] + d[i] * d[i];
            } else {
                real_t c_eff;
                if (i > 0 && b[i-1] < (real_t)0.) {
                    c_eff = a_snap[i-1] + d[i-1] * d[i-1];
                } else {
                    c_eff = c_snap[i];
                }
                a[i] = c_eff + d[i] * e[i];
            }
        }

        pb_mix(nl);
    }

    free(a_snap);
    free(c_snap);
    return (real_t)0;
}

PB_MAIN(kernel_s161)
