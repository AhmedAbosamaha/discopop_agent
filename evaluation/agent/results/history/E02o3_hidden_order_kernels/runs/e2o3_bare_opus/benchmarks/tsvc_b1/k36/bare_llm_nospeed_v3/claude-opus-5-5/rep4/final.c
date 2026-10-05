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
    /* Does AT1 read a v element written earlier in the same sweep (true recurrence)? */
    int dep = 0;
    #pragma omp parallel for reduction(||:dep)
    for (long i = 1; i < LEN_1D; i++) {
        long j1 = (long)(&AT1(v, i) - &v[0]);
        dep = dep || (j1 >= 1 && j1 < i);
    }

    real_t *tu = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    if (tu == NULL) dep = 1;

    for (int nl = 0; nl < R; nl++) {
        if (dep) {
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += AT1(v, i) * c[i];
                v[i] = AT2(u, i) * d[i] + c[i];
            }
        } else {
            /* pass 1: new u values (v is still entirely old here) */
            #pragma omp parallel for shared(tu)
            for (long i = 1; i < LEN_1D; i++) {
                tu[i] = u[i] + AT1(v, i) * c[i];
            }
            /* pass 2: v, reading new u for indices already updated (1..i), old u otherwise */
            #pragma omp parallel for shared(tu)
            for (long i = 1; i < LEN_1D; i++) {
                long j2 = (long)(&AT2(u, i) - &u[0]);
                real_t uv = (j2 >= 1 && j2 <= i) ? tu[j2] : AT2(u, i);
                v[i] = uv * d[i] + c[i];
            }
            /* pass 3: commit new u */
            #pragma omp parallel for shared(tu)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] = tu[i];
            }
        }
        pb_mix(nl);
    }
    free(tu);
    return (real_t)0;
}

PB_MAIN(kernel_k36)
