#include <stdlib.h>
#include "data.h"

real_t kernel_k31(void)
{
    const long o = off;
    const long f = far;
    real_t *uold = NULL;
    if (o >= 0 && f > 0) {
        uold = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    }

    for (int nl = 0; nl < iterations; nl++) {
        if (o >= 0) {
            /* snapshot of u: phase 2 needs pre-sweep values at i+far when far > 0 */
            if (f > 0) {
                #pragma omp parallel for default(none) shared(u, uold)
                for (long i = 0; i < LEN_1D; i++) {
                    uold[i] = u[i];
                }
            }
            /* phase 1: every u update reads v before this sweep wrote it (off >= 0) */
            #pragma omp parallel for default(none) shared(u, v, c) firstprivate(o)
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + o] * c[i];
            }
            /* phase 2: v from new u (index <= i) or old u (index > i) */
            #pragma omp parallel for default(none) shared(u, v, c, d, uold) firstprivate(f)
            for (long i = 1; i < LEN_1D; i++) {
                long j = i + f;
                real_t uv = (f > 0 && j < LEN_1D) ? uold[j] : u[j];
                v[i] = uv * d[i] + c[i];
            }
        } else {
            /* off < 0: genuine recurrence through v -> u -> v; keep serial */
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + o] * c[i];
                v[i] = u[i + f] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(uold);
    return (real_t)0;
}
