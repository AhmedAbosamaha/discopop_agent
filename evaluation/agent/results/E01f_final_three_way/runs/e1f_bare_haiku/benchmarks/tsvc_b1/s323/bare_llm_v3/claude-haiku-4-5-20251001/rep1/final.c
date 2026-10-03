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
        /* Pass 1: Compute delta[i] = c[i] * (d[i] + e[i]) in parallel
           This extracts the increment that will be added to b[i] in the prefix sum.
           delta[i] is private to each iteration; c, d, e are shared read-only. */
        real_t *delta = (real_t *)malloc(LEN_1D * sizeof(real_t));

        #pragma omp parallel for schedule(static) shared(c, d, e, delta) private(i)
        for (int i = 1; i < LEN_1D; i++) {
            delta[i] = c[i] * (d[i] + e[i]);
        }

        /* Pass 2: Sequential prefix sum to update b[i] = b[i-1] + delta[i]
           This maintains the original loop-carried dependence through b.
           b and delta are shared; i is private. */
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = b[i-1] + delta[i];
        }

        /* Pass 3: Compute a[i] = b[i-1] + c[i] * d[i] in parallel
           Each iteration is independent: reads b[i-1] (from pass 2, invariant per iteration),
           c[i], and d[i] (read-only arrays), and writes to a[i].
           a, b, c, d are shared; i is private. */
        #pragma omp parallel for schedule(static) shared(a, b, c, d) private(i)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }

        free(delta);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s323)
