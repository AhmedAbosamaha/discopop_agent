/* TSVC-2 loop s121, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s121.h"
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

static real_t kernel_s121(void)
{
    /* Snapshot buffer: holds the values a[] had before the current
     * activation of the inner loop started. The inner loop only ever
     * reads index i+1 before that index gets overwritten in the same
     * activation (writes proceed 0,1,2,...), so every read in the
     * original sequential loop effectively sees this pre-activation
     * snapshot, not anything produced earlier in the same activation.
     * Reading from the snapshot instead of from a[] directly removes
     * the anti-dependence between iterations and makes them independent.
     * Heap-allocated because LEN_1D can be huge in the verification builds. */
    real_t *old_a = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        memcpy(old_a, a, (size_t)LEN_1D * sizeof(real_t));
#pragma omp parallel for default(none) shared(a, b, old_a)
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;              /* declared inside the loop: per-iteration scratch, no clause needed */
            a[i] = old_a[j] + b[i];     /* each i writes a distinct a[i]; reads old_a[j] (pre-activation) and b[i] */
        }
        pb_mix(nl);
    }
    free(old_a);
    return (real_t)0;
}

PB_MAIN(kernel_s121)
