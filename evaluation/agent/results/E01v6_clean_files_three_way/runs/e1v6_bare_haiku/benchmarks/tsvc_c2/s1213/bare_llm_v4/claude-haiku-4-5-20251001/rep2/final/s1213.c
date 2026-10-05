#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Compute b values in parallel: each iteration reads a[i+1] and d[i] (from input),
        // writes to b[i]. No loop-carried dependency since a[i+1] is not updated in this loop.
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }
        // Compute a values in parallel: each iteration reads b[i-1] (computed above) and c[i],
        // writes to a[i]. No loop-carried dependency within this loop.
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
