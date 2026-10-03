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
    const long lo = (long)(off);
    const long lf = (long)(far);
    real_t *t = NULL;
    if (lo >= 0 && lf >= 0)
        t = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < R; nl++) {
        if (t != NULL) {
            /* new u, from old u and old v */
            #pragma omp parallel for shared(t) firstprivate(lo) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                t[i] = u[i] + v[i + lo] * c[i];
            }
            /* new v: old u[i+far] if far>0, new u[i] if far==0 */
            #pragma omp parallel for shared(t) firstprivate(lf) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                real_t uu = (lf > 0) ? u[i + lf] : t[i];
                v[i] = uu * d[i] + c[i];
            }
            #pragma omp parallel for shared(t) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
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
