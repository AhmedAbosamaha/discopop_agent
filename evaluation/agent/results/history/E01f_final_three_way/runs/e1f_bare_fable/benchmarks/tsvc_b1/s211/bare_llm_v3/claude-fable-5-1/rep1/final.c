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
    /* tmp[i] holds the new value of b[i] for one repetition.  The original loop
     * reads b[i-1] (already updated) and b[i+1] (not yet updated): computing all
     * new b values into tmp first, then forming a from tmp, removes both the
     * flow dependence through b[i-1] and the anti-dependence through b[i+1]. */
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        /* b[0] is never rewritten by the loop, so the "new" b[0] is the old one. */
        tmp[0] = b[0];
#pragma omp parallel for shared(b, d, e, tmp) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            tmp[i] = b[i + 1] - e[i] * d[i];
        }
#pragma omp parallel for shared(a, b, c, d, tmp) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = tmp[i - 1] + c[i] * d[i];
            b[i] = tmp[i];
        }
        pb_mix(nl);
    }
    free(tmp);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
