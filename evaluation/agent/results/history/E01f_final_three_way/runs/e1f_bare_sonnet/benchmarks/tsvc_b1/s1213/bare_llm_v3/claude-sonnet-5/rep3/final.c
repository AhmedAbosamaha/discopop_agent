/* TSVC-2 loop s1213, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s1213.h"
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

static real_t kernel_s1213(void)
{
    /* The inner loop as written has a true dependence through b[i-1] (written by
     * iteration i-1, read by iteration i) and a loop-carried reuse of a[i+1] (read by
     * iteration i before it is overwritten by iteration i+1). Unrolling the recurrence
     * in terms of the values a[], b[] hold BEFORE this sweep (call them a_old, b_old)
     * shows every iteration only ever needs those pre-sweep values, never another
     * iteration's freshly written one:
     *   b_new[i] = a_old[i+1]*d[i]                              (always; a[i+1] is not
     *              touched until iteration i+1 runs, so it's still the old value)
     *   a_new[i] = b_new[i-1] + c[i]
     *            = (i==1 ? b_old[0]            : a_old[i]*d[i-1]) + c[i]
     *     because b_new[i-1], for i-1>=1, equals a_old[i]*d[i-1] by the formula above
     *     applied one index earlier, and b[0] is never written by this loop, so for
     *     i==1 it is still exactly b_old[0].
     * So the dependence is removed by snapshotting a[] into a_old before the sweep and
     * having every iteration read only from that snapshot (plus the untouched b[0]),
     * while writing its own a[i]/b[i] -- no iteration reads another iteration's output
     * any more, so the sweep can run in any order/partition.
     * a_old is heap-allocated (LEN_1D can be up to 192,000,000) and reused across the
     * R repetitions to avoid repeated malloc/free overhead. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));

        /* a, b, c, d, a_old: shared arrays. Each iteration i writes only a[i] and b[i]
         * (distinct per i, no overlap), and reads only from the read-only-this-sweep
         * a_old/c/d plus the never-written-by-this-loop b[0] -- no two iterations touch
         * a common location where at least one of them writes, so this is race-free
         * under any schedule/order. prev is scratch declared inside the loop body, so
         * it is private by construction and needs no clause. */
        #pragma omp parallel for default(none) shared(a, b, c, d, a_old) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            real_t prev = (i == 1) ? b[0] : a_old[i] * d[i-1];
            a[i] = prev + c[i];
            b[i] = a_old[i+1] * d[i];
        }
        pb_mix(nl);
    }

    free(a_old);
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
