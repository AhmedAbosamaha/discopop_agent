#include <stdlib.h>
#include "data.h"

real_t kernel_k31(void)
{
    long o = off;
    long f = far;
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        if (f > 0) {
            /* u[i+far] is always the pre-sweep value: new v computable up front */
            #pragma omp parallel for default(none) shared(u, c, d, tmp) firstprivate(f) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                tmp[i] = u[i + f] * d[i] + c[i];
            }
            /* v[i+off] is new only if it was written earlier in the sweep */
            #pragma omp parallel for default(none) shared(u, v, c, tmp) firstprivate(o) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                long j = i + o;
                real_t vv = (o < 0 && j >= 1) ? tmp[j] : v[j];
                u[i] += vv * c[i];
            }
            #pragma omp parallel for default(none) shared(v, tmp) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = tmp[i];
            }
        } else if (o >= 0) {
            /* v[i+off] is always the pre-sweep value */
            #pragma omp parallel for default(none) shared(u, v, c) firstprivate(o) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + o] * c[i];
            }
            /* u[i+far] (far <= 0) is the updated value (u[0] never changes) */
            #pragma omp parallel for default(none) shared(u, v, c, d) firstprivate(f) schedule(static)
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u[i + f] * d[i] + c[i];
            }
        } else {
            /* genuine recurrence through u: keep serial order */
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + o] * c[i];
                v[i] = u[i + f] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
