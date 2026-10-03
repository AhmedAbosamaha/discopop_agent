/* Kernel k36. */
#include "tsvc_b1/k36.h"
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

static real_t kernel_k36(void)
{
    real_t *uold = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        /* snapshot of u before this sweep (for reads ahead of i) */
#pragma omp parallel for schedule(static) shared(uold)
        for (long i = 0; i < LEN_1D; i++) {
            uold[i] = u[i];
        }
        /* u update: reads v, which is not modified until the next loop */
#pragma omp parallel for schedule(static)
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += AT1(v, i) * c[i];
        }
        /* v update: index <= i sees updated u, index > i sees old u */
#pragma omp parallel for schedule(static) shared(uold)
        for (long i = 1; i < LEN_1D; i++) {
            long j = (long)(&AT2(u, i) - &u[0]);
            real_t x = (j <= i) ? u[j] : uold[j];
            v[i] = x * d[i] + c[i];
        }
        pb_mix(nl);
    }
    free(uold);
    return (real_t)0;
}

PB_MAIN(kernel_k36)
