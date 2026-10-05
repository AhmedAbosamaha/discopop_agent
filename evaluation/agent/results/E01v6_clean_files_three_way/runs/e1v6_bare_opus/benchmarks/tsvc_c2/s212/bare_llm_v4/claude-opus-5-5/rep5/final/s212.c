#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* b reads the OLD a[i+1]: do all b updates before any a update */
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
