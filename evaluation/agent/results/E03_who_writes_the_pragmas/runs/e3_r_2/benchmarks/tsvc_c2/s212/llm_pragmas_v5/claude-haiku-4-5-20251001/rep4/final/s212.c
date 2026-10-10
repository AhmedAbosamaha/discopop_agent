#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: update b using original a values
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }

        // Second pass: update a
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
