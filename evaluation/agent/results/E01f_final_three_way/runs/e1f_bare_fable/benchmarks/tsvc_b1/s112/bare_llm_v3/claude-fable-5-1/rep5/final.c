/* TSVC-2 loop s112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s112.h"

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

#include <stdlib.h>

/* Scratch buffer that breaks the anti-dependence of the backward recurrence:
 * the original loop reads a[i] before iteration i-1 overwrites it, so every
 * a[i+1] is old_a[i] + b[i].  We compute all sums into tmp first, then copy. */
static real_t *s112_tmp = NULL;

static real_t kernel_s112(void)
{
    if (s112_tmp == NULL) {
        s112_tmp = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    }
    real_t *tmp = s112_tmp;

    for (int nl = 0; nl < R; nl++) {
        /* pass 1: tmp[i] = old a[i] + b[i]  (reads only a and b) */
        #pragma omp parallel for shared(a, b, tmp)
        for (int i = 0; i < LEN_1D - 1; i++) {
            tmp[i] = a[i] + b[i];
        }
        /* pass 2: a[i+1] = tmp[i]  (distinct a elements per iteration) */
        #pragma omp parallel for shared(a, tmp)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = tmp[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s112)
