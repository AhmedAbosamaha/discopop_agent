/* TSVC-2 loop s244, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s244.h"

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

static real_t kernel_s244(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Phase 1: Compute a[i] for all i in parallel using old b values.
         * No loop-carried dependence: each iteration i only writes a[i],
         * and no other iteration reads a[i]. */
        #pragma omp parallel for schedule(static) shared(a,b,c,d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
        }

        /* Phase 2: Update b[i] for all i in parallel.
         * No loop-carried dependence: each iteration i only writes b[i],
         * and no other iteration reads b[i]. */
        #pragma omp parallel for schedule(static) shared(b,c,d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            b[i] = c[i] + b[i];
        }

        /* Phase 3: Compute a[LEN_1D-1] using updated b[LEN_1D-2].
         * This corresponds to line 3 of the last iteration (i=LEN_1D-2)
         * from the original loop. */
        a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];

        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s244)
