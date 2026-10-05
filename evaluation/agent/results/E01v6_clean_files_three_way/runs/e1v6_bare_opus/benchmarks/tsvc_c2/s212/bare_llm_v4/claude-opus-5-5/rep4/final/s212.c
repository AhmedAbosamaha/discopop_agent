#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* b reads the original (not yet scaled) a[i+1]: do all of b first */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, d)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }
        #pragma omp parallel for schedule(static) default(none) shared(a, c)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
