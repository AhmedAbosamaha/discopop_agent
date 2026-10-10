#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    real_t *old_a = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        // Save old values of a before they are updated
        #pragma omp parallel for shared(old_a) 
        for (int i = 0; i < LEN_1D; i++) {
            old_a[i] = a[i];
        }
        // Pass 1: compute new a values (parallelizable: no cross-iteration dependence)
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        // Pass 2: compute b using the old a values (parallelizable: each iteration accesses different b[i])
        #pragma omp parallel for shared(old_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += old_a[i + 1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(old_a);
    return (real_t)0;
}
