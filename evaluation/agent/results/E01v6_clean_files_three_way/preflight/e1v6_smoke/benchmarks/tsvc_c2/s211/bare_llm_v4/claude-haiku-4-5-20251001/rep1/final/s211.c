#include "data.h"
#include <stdlib.h>

real_t kernel_s211(void)
{
    // Allocate temporary buffer for b values to break anti-dependence
    real_t *b_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute b values in parallel using temporary buffer
        // Each iteration i reads b[i+1] (original values, no race) and writes to b_temp[i]
        // No loop-carried dependence: iteration i reads b[i+1], iteration i+1 writes to b_temp[i+1] (not shared)
        #pragma omp parallel for schedule(static) shared(b_temp, b, e, d)
        for (int i = 1; i < LEN_1D-1; i++) {
            b_temp[i] = b[i + 1] - e[i] * d[i];
        }

        // Copy computed b values back to the main b array
        #pragma omp parallel for schedule(static) shared(b_temp, b)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_temp[i];
        }

        // Phase 2: Compute a values in parallel using updated b
        // Each iteration i writes to a[i] and reads b[i-1] (computed in phase 1)
        // No conflicts: each iteration accesses unique a[i], and b is now stable
        #pragma omp parallel for schedule(static) shared(a, b, c, d)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(b_temp);
    return (real_t)0;
}
