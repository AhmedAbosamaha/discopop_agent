#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute all b[i] values in parallel
        // No loop-carried dependence: each iteration reads a[i+1] (unchanged in this phase)
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }

        // Phase 2: Compute all a[i] values in parallel
        // No loop-carried dependence: each iteration reads b[i-1] (fully computed in phase 1)
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
