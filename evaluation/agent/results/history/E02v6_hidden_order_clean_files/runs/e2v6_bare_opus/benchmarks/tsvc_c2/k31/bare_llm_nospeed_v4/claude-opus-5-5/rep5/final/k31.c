#include <stdlib.h>
#include "data.h"

real_t kernel_k31(void)
{
    const long o = off;
    const long f = far;
    const int indep = (o >= 0 && f >= 0);
    real_t *t = NULL;
    if (indep) {
        t = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    }
    for (int nl = 0; nl < iterations; nl++) {
        if (indep && t != NULL) {
            /* phase 1: new u (reads only pre-loop values of u and v) */
            #pragma omp parallel for default(none) shared(t, u, v, c) firstprivate(o) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                t[i] = u[i] + v[i + o] * c[i];
            }
            /* phase 2: new v (reads pre-loop u[i+f], or new u[i] when f==0) */
            #pragma omp parallel for default(none) shared(t, u, v, c, d) firstprivate(f) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                real_t uu = (f == 0) ? t[i] : u[i + f];
                v[i] = uu * d[i] + c[i];
            }
            /* phase 3: commit new u */
            #pragma omp parallel for default(none) shared(t, u) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] = t[i];
            }
        } else {
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + o] * c[i];
                v[i] = u[i + f] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(t);
    return (real_t)0;
}
