/* Kernel k31. */
#include "tsvc_b1/k31.h"
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

static real_t kernel_k31(void)
{
    real_t *x = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    int par_ok = (x != NULL) && ((long)(off) >= 0) && ((long)(far) >= 0);
    for (int nl = 0; nl < R; nl++) {
        if (par_ok) {
            if ((long)(far) > 0) {
                /* snapshot old u[i+far] before any u is updated */
                #pragma omp parallel for shared(x, u)
                for (long i = 1; i < LEN_1D; i++) {
                    x[i] = u[i + far];
                }
            }
            /* v is not written here, so v[i+off] is the old value */
            #pragma omp parallel for shared(u, v, c)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }
            #pragma omp parallel for shared(x, u, v, c, d)
            for (long i = 1; i < LEN_1D; i++) {
                real_t ui = ((long)(far) > 0) ? x[i] : u[i];
                v[i] = ui * d[i] + c[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
                v[i] = u[i + far] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    free(x);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
