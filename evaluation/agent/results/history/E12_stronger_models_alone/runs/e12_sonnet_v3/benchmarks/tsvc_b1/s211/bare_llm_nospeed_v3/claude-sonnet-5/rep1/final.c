/* TSVC-2 loop s211, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s211.h"
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

static real_t kernel_s211(void)
{
    /* The sequential loop reads b[i-1] after it has already been overwritten (at
     * iteration i-1) and reads b[i+1] before it has been touched (it is only written
     * at iteration i+1, which hasn't run yet). So every b[i-1]/b[i+1] read in the
     * original loop resolves to a value derivable from b as it stood BEFORE this
     * sweep started (call that b_old):
     *   b[i]  = b_old[i+1] - e[i]*d[i]                      (b[i+1] is never written
     *                                                         before iteration i runs)
     *   a[i]  = b_old[i]   - e[i-1]*d[i-1]  + c[i]*d[i]      for i >= 2
     *   a[1]  = b_old[0]                   + c[1]*d[1]      (b[0] is never written
     *                                                         by this loop)
     * Taking a snapshot of b into a heap buffer before the i-loop and reading only
     * from that snapshot removes the cross-iteration dependence entirely: each i
     * then only reads b_old/c/d/e and writes its own a[i], b[i], independent of
     * every other i. */
    real_t *b_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for default(none) shared(b, b_old)
        for (int i = 0; i < LEN_1D; i++) {
            b_old[i] = b[i];
        }
        #pragma omp parallel for default(none) shared(a, b, b_old, c, d, e)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = (i == 1 ? b_old[0] : b_old[i] - e[i - 1] * d[i - 1]) + c[i] * d[i];
            b[i] = b_old[i + 1] - e[i] * d[i];
        }
        pb_mix(nl);
    }
    free(b_old);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
