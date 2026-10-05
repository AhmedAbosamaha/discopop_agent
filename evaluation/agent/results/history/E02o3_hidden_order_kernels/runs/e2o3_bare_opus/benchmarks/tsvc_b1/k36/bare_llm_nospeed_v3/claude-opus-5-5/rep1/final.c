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
    /* Classify the access offsets once (they do not depend on data). */
    int recur = 0, need_old = 0;
    #pragma omp parallel for reduction(|:recur, need_old)
    for (long i = 1; i < LEN_1D; i++) {
        long j1 = (long)(&AT1(v, i) - &v[0]);
        long j2 = (long)(&AT2(u, i) - &u[0]);
        if (j1 >= 1 && j1 < i) recur = 1;
        if (j2 > i && j2 < LEN_1D) need_old = 1;
    }

    real_t *uold = NULL;
    if (need_old && !recur)
        uold = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
      if (recur) {
        /* true recurrence through v: must stay serial for identical rounding */
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += AT1(v, i) * c[i];
            v[i] = AT2(u, i) * d[i] + c[i];
        }
      } else {
        if (need_old) {
            #pragma omp parallel for shared(uold)
            for (long i = 0; i < LEN_1D; i++)
                uold[i] = u[i];
        }
        /* u update reads only the old v (not yet written this repetition) */
        #pragma omp parallel for
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += AT1(v, i) * c[i];
        }
        /* v update: new u for j2 <= i, old u for j2 > i (as the serial order saw) */
        #pragma omp parallel for shared(uold, need_old)
        for (long i = 1; i < LEN_1D; i++) {
            long j2 = (long)(&AT2(u, i) - &u[0]);
            real_t x = (need_old && j2 > i && j2 < LEN_1D) ? uold[j2] : AT2(u, i);
            v[i] = x * d[i] + c[i];
        }
      }
        pb_mix(nl);
    }

    free(uold);
    return (real_t)0;
}

PB_MAIN(kernel_k36)
