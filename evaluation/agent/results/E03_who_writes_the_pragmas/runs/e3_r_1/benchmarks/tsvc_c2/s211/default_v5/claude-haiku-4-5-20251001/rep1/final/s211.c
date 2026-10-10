#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s211(void)
{
    // Allocate once outside the repeated loop
    real_t *b_orig = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy b at the start of each activation
        memcpy(b_orig, b, LEN_1D * sizeof(real_t));

        // First pass: compute new b values using original b[i+1]
        #pragma omp parallel for shared(b_orig) 
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_orig[i + 1] - e[i] * d[i];
        }

        // Second pass: compute a values using updated b[i-1]
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(b_orig);
    return (real_t)0;
}
