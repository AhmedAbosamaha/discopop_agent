/* TSVC-2 loop s322, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s322.h"

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

static real_t kernel_s322(void)
{
    real_t *temp = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        /* Compute products in parallel: no iteration writes values that another reads */
        #pragma omp parallel for shared(a, b, c, temp)
        for (int i = 2; i < LEN_1D; i++) {
            temp[i] = a[i - 1] * b[i] + a[i - 2] * c[i];
        }

        /* Accumulate in parallel: each thread updates independent a[i] */
        #pragma omp parallel for shared(a, temp)
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a[i] + temp[i];
        }

        pb_mix(nl);
    }

    free(temp);
    return (real_t)0;
}

PB_MAIN(kernel_s322)
