/* Kernel k17. */
#include "tsvc_b1/k17.h"

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

static real_t kernel_k17(void)
{
    real_t *temp_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *temp_v = (real_t *)malloc(LEN_1D * sizeof(real_t));

    #pragma omp parallel for 
    for (int nl = 0; nl < R; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            temp_u[i] = v[kv[i]] * c[i];
            temp_v[i] = u[ku[i]] * d[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += temp_u[i];
            v[jv[i]] += temp_v[i];
        }
        pb_mix(nl);
    }

    free(temp_u);
    free(temp_v);
    return (real_t)0;
}

PB_MAIN(kernel_k17)
