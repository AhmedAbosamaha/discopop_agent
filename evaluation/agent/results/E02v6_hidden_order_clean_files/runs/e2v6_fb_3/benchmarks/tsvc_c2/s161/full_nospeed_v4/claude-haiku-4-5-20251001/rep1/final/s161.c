#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: write-path iterations (b[i] < 0)
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        // Phase 2: read-path iterations (b[i] >= 0)
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
