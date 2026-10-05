/* TSVC-2 loop s112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s112.h"
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

static real_t kernel_s112(void)
{
    /* The original backward loop reads a[i] before iteration i-1 overwrites it: an
     * anti-dependence only.  Every result is a_new[i+1] = a_old[i] + b[i], so compute
     * all sums into a heap temporary (reads only), then write them back (disjoint
     * writes).  Order within each pass is irrelevant. */
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for shared(a, b, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            tmp[i] = a[i] + b[i];
        }
        #pragma omp parallel for shared(a, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = tmp[i];
        }
        pb_mix(nl);
    }
    free(tmp);
    return (real_t)0;
}

PB_MAIN(kernel_s112)
