#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    real_t *temp_a = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute new a values in parallel based on current b
        #pragma omp parallel for shared(temp_a, b, c, d)
        for (int i = 0; i < LEN_1D-1; i++) {
            temp_a[i] = b[i] * c[i] * d[i];
        }
        // Phase 2: Compute new b values in parallel using new a and old a[i+1]
        #pragma omp parallel for shared(temp_a, a, b, d)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = temp_a[i] * a[i+1] * d[i];
        }
        // Phase 3: Update a in parallel with new values
        #pragma omp parallel for shared(temp_a, a)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = temp_a[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp_a);
    return (real_t)0;
}
