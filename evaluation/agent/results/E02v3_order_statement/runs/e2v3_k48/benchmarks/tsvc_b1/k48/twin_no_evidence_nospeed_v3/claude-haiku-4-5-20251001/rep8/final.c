/* Kernel k48. */
#include "tsvc_b1/k48.h"

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

static real_t kernel_k48(void)
{
    real_t* temp = (real_t*)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            temp[i] = u[ku[i]];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
        }
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = temp[i] * d[i] + c[i];
        }
        pb_mix(nl);
    }

    free(temp);
    return (real_t)0;
}

PB_MAIN(kernel_k48)
