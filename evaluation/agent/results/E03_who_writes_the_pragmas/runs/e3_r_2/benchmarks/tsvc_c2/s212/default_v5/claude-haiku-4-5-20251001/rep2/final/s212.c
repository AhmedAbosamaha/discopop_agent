#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First loop: update b using original a values (before a is modified)
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }

        // Second loop: update a values (no dependence: each iteration writes a[i])
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
