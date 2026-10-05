/* TSVC-2 loop s241, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s241.h"
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

static real_t kernel_s241(void)
{
    real_t *t = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        /* reads only old a; writes b[i] and t[i] (new a[i]) */
        #pragma omp parallel for shared(t) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t ai = b[i] * c[i  ] * d[i];
            t[i] = ai;
            b[i] = ai * a[i+1] * d[i];
        }
        #pragma omp parallel for shared(t) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = t[i];
        }
        pb_mix(nl);
    }
    free(t);
    return (real_t)0;
}

PB_MAIN(kernel_s241)
