/* TSVC-2 loop s481, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s481.h"

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

static real_t kernel_s481(void)
{
    for (int nl = 0; nl < R; nl++) {
        // Check for early exit before parallelization
        // d[i] is not modified by the inner loop, so this check has the same effect as before
        for (int i = 0; i < LEN_1D; i++) {
            if (d[i] < (real_t)0.) {
                exit(0);
            }
        }

        // Parallelize the main kernel loop
        // Each iteration i only reads b[i], c[i] and modifies a[i] at index i
        // No cross-iteration dependencies: safe to run in any order
        #pragma omp parallel for shared(a, b, c)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] += b[i] * c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s481)
