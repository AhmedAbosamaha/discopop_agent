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
    #pragma omp parallel for 
    for (int nl = 0; nl < R; nl++) {
        u[ju[1]] += v[kv[1]] * c[1];
        for (long i = 1; i < LEN_1D - 1; i++) {
            v[jv[i]] += u[ku[i]] * d[i];
            u[ju[i+1]] += v[kv[i+1]] * c[i+1];
        }
        v[jv[LEN_1D-1]] += u[ku[LEN_1D-1]] * d[LEN_1D-1];
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k17)
