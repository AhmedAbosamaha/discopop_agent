/* Kernel k36. */
#include "tsvc_b1/k36.h"

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
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: v from the not-yet-updated u (AT2 reads ahead of i) */
        #pragma omp parallel for schedule(static) default(shared)
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = AT2(u, i) * d[i] + c[i];
        }
        /* pass 2: u from the already-updated v (AT1 reads behind i) */
        #pragma omp parallel for schedule(static) default(shared)
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += AT1(v, i) * c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k36)
