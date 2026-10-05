/* TSVC-2 loop s323, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s323.h"
#include <stdlib.h>

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
    /* The inner loop is a first-order linear recurrence through b:
     * a[i] = b[i-1] + c[i]*d[i]; b[i] = a[i] + c[i]*e[i]
     * so b[i] = b[i-1] + c[i]*d[i] + c[i]*e[i]. Unrolling the recurrence:
     *   b[i] = b0 + sum_{j=1}^{i} (c[j]*d[j] + c[j]*e[j])
     *   a[i] = b0 + sum_{j=1}^{i-1} (c[j]*d[j] + c[j]*e[j]) + c[i]*d[i]
     * where b0 = b[0] is loop-invariant (this loop never writes b[0];
     * only pb_mix touches it, strictly between repetitions). That turns
     * the per-i dependence into: an independent per-i increment, a
     * prefix sum of those increments (the only part that still carries
     * a value from one index to the next), and an independent per-i
     * reconstruction of a[i]/b[i] from b0 and the prefix sum.
     * t is heap-allocated (LEN_1D can be up to 192e6) and reused across
     * repetitions of nl. */
    real_t *t = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        real_t b0 = b[0];

        /* Phase 1: per-i increment of the b-recurrence; indices disjoint,
         * no dependence between iterations. */
        #pragma omp parallel for default(none) shared(c, d, e, t)
        for (int i = 1; i < LEN_1D; i++) {
            t[i] = c[i] * d[i] + c[i] * e[i];
        }

        /* Phase 2: prefix-sum the increments in place. This is the one
         * true remaining dependence (t[i] needs t[i-1]); it is a single
         * add per index, left sequential and not parallelized. */
        for (int i = 2; i < LEN_1D; i++) {
            t[i] += t[i - 1];
        }

        /* Phase 3: reconstruct a[i], b[i] from b0 and the prefix sum.
         * bprev stands in for the b[i-1] the original loop would have
         * read; each i writes only a[i]/b[i], so iterations are
         * independent again. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e, t) firstprivate(b0)
        for (int i = 1; i < LEN_1D; i++) {
            real_t bprev = (i == 1) ? b0 : b0 + t[i - 1];
            a[i] = bprev + c[i] * d[i];
            b[i] = a[i] + c[i] * e[i];
        }

        pb_mix(nl);
    }

    free(t);
    return (real_t)0;
}

PB_MAIN(kernel_s323)
