#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute a[i] and update b[i] (parallel)
        #pragma omp parallel for shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }

        // Phase 2: Update a[i+1] using updated b[i] (parallel)
        #pragma omp parallel for shared(a, b, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i+1] = b[i] + a[i+1] * d[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
