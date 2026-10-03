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
    real_t *t = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    const long n = LEN_1D;
    const long offv = (long)(off);
    const long farv = (long)(far);
    for (int nl = 0; nl < R; nl++) {
        if (t != NULL && offv >= 0 && farv >= 0) {
            /* pass 1: new u into t (reads only old u, old v) */
            #pragma omp parallel for shared(t) firstprivate(n, offv) schedule(static)
            for (long i = 1; i < n; i++) {
                t[i] = u[i] + v[i + offv] * c[i];
            }
            /* pass 2: new v (u still old; far==0 uses the fresh u[i]) */
            #pragma omp parallel for shared(t) firstprivate(n, farv) schedule(static)
            for (long i = 1; i < n; i++) {
                real_t uu = (farv == 0) ? t[i] : u[i + farv];
                v[i] = uu * d[i] + c[i];
            }
            /* pass 3: commit new u */
            #pragma omp parallel for shared(t) firstprivate(n) schedule(static)
            for (long i = 1; i < n; i++) {
                u[i] = t[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
                v[i] = u[i + far] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    free(t);
    return (real_t)0;
}

PB_MAIN(kernel_k31)
