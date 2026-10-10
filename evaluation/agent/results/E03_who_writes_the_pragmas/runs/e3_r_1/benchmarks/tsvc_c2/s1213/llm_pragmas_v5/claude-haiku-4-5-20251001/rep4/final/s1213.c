#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute all b values in parallel
        // Each iteration reads a[i+1] (different for each i) and writes b[i] (different for each i).
        // No loop-carried dependence: a and b are accessed at independent indices.
        // Uses a values from previous outer iteration.
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }

        // Phase 2: Compute all a values in parallel
        // Each iteration reads b[i-1] (different for each i) and writes a[i] (different for each i).
        // No loop-carried dependence: a and b are accessed at independent indices.
        // Uses newly computed b values from phase 1.
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
