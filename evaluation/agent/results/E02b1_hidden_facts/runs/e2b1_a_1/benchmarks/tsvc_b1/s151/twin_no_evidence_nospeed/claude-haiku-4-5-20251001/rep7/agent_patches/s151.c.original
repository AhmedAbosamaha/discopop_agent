/* TSVC-2 loop s151, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s151.h"

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

void s151s(real_t a[LEN_1D], real_t b[LEN_1D],  int m)
{
    if (m == 1) {
        /* Restructure to expose Do-All parallelism by removing loop-carried dependence.
         * Original: a[i] = a[i+1] + b[i] (backward dependence on a[i+1])
         * Restructured: a[i] = a[LEN_1D-1] + suffix_sum[i] where
         * suffix_sum[i] = b[i] + b[i+1] + ... + b[LEN_1D-2] (suffix sum of b)
         * This makes the main loop independent across iterations.
         */
        real_t *suffix_sum = malloc((LEN_1D - 1) * sizeof(real_t));

        /* Compute suffix sum in reverse (backward loop with dependence) */
        suffix_sum[LEN_1D - 2] = b[LEN_1D - 2];
        for (int i = LEN_1D - 3; i >= 0; i--) {
            suffix_sum[i] = suffix_sum[i + 1] + b[i];
        }

        /* Main loop: independent assignment, no loop-carried dependence (Do-All) */
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i] = a[LEN_1D - 1] + suffix_sum[i];
        }

        free(suffix_sum);
    } else {
        /* Original loop for other values of m */
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i] = a[i + m] + b[i];
        }
    }
}

static real_t kernel_s151(void)
{
    for (int nl = 0; nl < R; nl++) {
        s151s(a, b,  1);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s151)
