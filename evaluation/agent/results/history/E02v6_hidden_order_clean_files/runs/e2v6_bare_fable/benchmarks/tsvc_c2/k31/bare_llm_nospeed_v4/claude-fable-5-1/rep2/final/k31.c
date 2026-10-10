#include <stdlib.h>
#include "data.h"

real_t kernel_k31(void)
{
    long n = LEN_1D;
    real_t *tmp = NULL;

    if (off >= 0 && far > 0) {
        tmp = (real_t *)malloc((size_t)n * sizeof(real_t));
    }

    for (int nl = 0; nl < iterations; nl++) {
        if (off >= 0 && far > 0) {
            /* both reads see pre-sweep values of u and v */
            if (tmp == NULL) {
                for (long i = 1; i < n; i++) {
                    u[i] += v[i + off] * c[i];
                    v[i] = u[i + far] * d[i] + c[i];
                }
            } else {
#pragma omp parallel for default(none) shared(u, c, d, tmp, n, far)
                for (long i = 1; i < n; i++) {
                    tmp[i] = u[i + far] * d[i] + c[i];
                }
#pragma omp parallel for default(none) shared(u, v, c, n, off)
                for (long i = 1; i < n; i++) {
                    u[i] += v[i + off] * c[i];
                }
#pragma omp parallel for default(none) shared(v, tmp, n)
                for (long i = 1; i < n; i++) {
                    v[i] = tmp[i];
                }
            }
        } else if (off >= 0) {
            /* far <= 0: u reads old v, v reads new u */
#pragma omp parallel for default(none) shared(u, v, c, n, off)
            for (long i = 1; i < n; i++) {
                u[i] += v[i + off] * c[i];
            }
#pragma omp parallel for default(none) shared(u, v, c, d, n, far)
            for (long i = 1; i < n; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }
        } else if (far > 0) {
            /* off < 0: v reads old u, u reads new v */
#pragma omp parallel for default(none) shared(u, v, c, d, n, far)
            for (long i = 1; i < n; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }
#pragma omp parallel for default(none) shared(u, v, c, n, off)
            for (long i = 1; i < n; i++) {
                u[i] += v[i + off] * c[i];
            }
        } else {
            /* off < 0, far <= 0: recurrence u[i] <- v[i+off] <- u[i-k],
               k = -(off+far) >= 1.  Residue classes mod k are independent
               chains; chain r owns u[i], i == r (mod k), and v[i+off]. */
            long k = -(off + far);
#pragma omp parallel for default(none) shared(u, v, c, d, n, off, far, k)
            for (long r = 1; r <= k; r++) {
                for (long i = r; i < n; i += k) {
                    long j = i + off;
                    if (j >= 1) {
                        v[j] = u[j + far] * d[j] + c[j];
                    }
                    u[i] += v[j] * c[i];
                }
            }
            /* v[j] for j in [max(1, n+off), n) feed no u in this sweep */
            long lo = n + off;
            if (lo < 1) lo = 1;
#pragma omp parallel for default(none) shared(u, v, c, d, n, far, lo)
            for (long j = lo; j < n; j++) {
                v[j] = u[j + far] * d[j] + c[j];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(tmp);
    return (real_t)0;
}
