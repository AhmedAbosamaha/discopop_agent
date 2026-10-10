#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy current values of a to enable parallelization
        #pragma omp parallel for shared(a_copy) 
        for (int i = 0; i < LEN_1D; i++) {
            a_copy[i] = a[i];
        }

        // Compute new values reading from copy, writing to original
        // Removes loop-carried dependence: each iteration i reads a_copy[i+1]
        // (unchanged during loop) and writes a[i] (not read by other iterations)
        #pragma omp parallel for shared(a_copy) 
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;
            a[i] = a_copy[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_copy);
    return (real_t)0;
}
