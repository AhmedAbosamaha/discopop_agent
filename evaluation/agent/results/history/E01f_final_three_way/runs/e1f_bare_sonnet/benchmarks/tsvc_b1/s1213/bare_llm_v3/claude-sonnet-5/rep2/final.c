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
    /* old_a holds a snapshot of a[] taken before each i-loop runs: with the original
     * sequential order, a[i] = b[i-1]+c[i] actually consumes b[i-1] = a[i]_old*d[i-1]
     * (written by iteration i-1 just before), and b[i] = a[i+1]*d[i] always reads the
     * pre-loop value of a[i+1] (iteration i+1 hasn't run yet). So every new a[i]/b[i]
     * is a function of values that existed before the i-loop started; snapshotting
     * those removes the apparent i-1 -> i dependence (it was a reused location, not a
     * value that must flow through the loop) and lets all i be computed independently.
     * Heap-allocated because LEN_1D can be very large. */
    real_t *old_a = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        real_t b0 = b[0];
        memcpy(old_a, a, (size_t)LEN_1D * sizeof(real_t));

        #pragma omp parallel for default(none) shared(a, b, c, d, old_a) firstprivate(b0) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            /* a[i]: for i==1, b[0] was never written by this loop, so it's just the
             * pre-loop b0. For i>=2, b[i-1] = old_a[i]*d[i-1] (derived above). */
            if (i == 1) {
                a[i] = b0 + c[i];
            } else {
                a[i] = old_a[i]*d[i-1] + c[i];
            }
            /* b[i]: always reads the pre-loop value of a[i+1]. */
            b[i] = old_a[i+1]*d[i];
        }
        pb_mix(nl);
    }

    free(old_a);
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
