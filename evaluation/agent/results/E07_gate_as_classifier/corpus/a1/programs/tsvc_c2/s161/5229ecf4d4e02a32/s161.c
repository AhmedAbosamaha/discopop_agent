#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Pass 1: Compute all c[i+1] values
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        // Pass 2: Compute all a[i] values using updated c
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
