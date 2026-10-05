/* TSVC-2 loop s243, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s243.h"
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

static real_t kernel_s243(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Save snapshot of array a at loop start to remove loop-carried dependence on a[i+1].
         * Each iteration i needs to read a[i+1] as it existed before any inner loop iteration
         * modified it. By reading from a saved copy, all iterations see a consistent state
         * and can run in parallel without races. */
        real_t *a_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(a_prev, a, LEN_1D * sizeof(real_t));

        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_prev[i+1] * d[i];
        }
        free(a_prev);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s243)
