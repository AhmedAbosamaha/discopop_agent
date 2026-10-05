/* TSVC-2 loop s252, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s252.h"

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

static real_t kernel_s252(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Base case: a[0] = b[0]*c[0] + 0 */
        a[0] = b[0] * c[0];

        /* Parallel loop: a[i] = b[i]*c[i] + b[i-1]*c[i-1]
         * Loop-carried dependency on t is eliminated by computing each a[i]
         * directly from previous array elements instead of a scalar variable.
         * Each iteration is now independent and can run in any order.
         */
        #pragma omp parallel for schedule(static) shared(a, b, c) private(i)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i] * c[i] + b[i-1] * c[i-1];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s252)
