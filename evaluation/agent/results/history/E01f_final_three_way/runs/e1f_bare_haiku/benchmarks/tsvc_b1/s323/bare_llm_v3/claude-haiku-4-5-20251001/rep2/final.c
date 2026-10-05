/* TSVC-2 loop s323, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s323.h"

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

static real_t kernel_s323(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* First loop: compute a[i] from b[i-1] and c[i]*d[i].
         * No loop-carried dependence: each iteration reads b[i-1] (different index)
         * and doesn't write any b values.
         * Variables: i is loop-private by default, a[i] is written only by this iteration,
         * b, c, d are shared and read-only. */
        #pragma omp parallel for \
            shared(a, b, c, d) \
            private(i)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }

        /* Second loop: compute b[i] from newly computed a[i] and c[i]*e[i].
         * No loop-carried dependence: each iteration reads a[i] (same index it computes from)
         * and writes b[i] (same index), with no values flowing between iterations.
         * Variables: i is loop-private by default, b[i] is written only by this iteration,
         * a, c, e are shared and read-only. */
        #pragma omp parallel for \
            shared(a, b, c, e) \
            private(i)
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = a[i] + c[i] * e[i];
        }

        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s323)
