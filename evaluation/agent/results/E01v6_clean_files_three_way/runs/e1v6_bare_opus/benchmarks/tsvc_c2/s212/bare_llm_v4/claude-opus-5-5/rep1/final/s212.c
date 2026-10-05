#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* reads old a[i+1] before any a is updated */
        #pragma omp parallel for default(none) shared(a, b, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }
        #pragma omp parallel for default(none) shared(a, c) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
