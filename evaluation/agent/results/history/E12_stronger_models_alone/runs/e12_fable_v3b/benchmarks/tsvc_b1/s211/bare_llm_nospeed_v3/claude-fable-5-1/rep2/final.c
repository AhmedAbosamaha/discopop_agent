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
    /* bn[i] holds the new value of b[i] for one repetition, computed from the
     * old b so that neither pass carries a dependence between iterations. */
    real_t *bn = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        if (LEN_1D > 2) {
            /* Pass 1: new b into bn, reading only the old b (no writes to b). */
#pragma omp parallel for shared(b, d, e, bn)
            for (int i = 1; i < LEN_1D-1; i++) {
                bn[i] = b[i + 1] - e[i] * d[i];
            }
            /* a[1] uses b[0], which the kernel never writes. */
            a[1] = b[0] + c[1] * d[1];
            /* Pass 2: a[i] from the new b[i-1] (= bn[i-1]), and commit b. bn is read-only here. */
#pragma omp parallel for shared(a, b, c, d, bn)
            for (int i = 2; i < LEN_1D-1; i++) {
                a[i] = bn[i - 1] + c[i] * d[i];
                b[i] = bn[i];
            }
            b[1] = bn[1];
        }
        pb_mix(nl);
    }
    free(bn);
    return (real_t)0;
}

PB_MAIN(kernel_s211)
