#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    // Allocate buffer outside loop to save old a values (b has no loop-carried dependence)
    real_t* old_a = (real_t*)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy a to preserve old values for a[i+1] reads in parallel loop
        #pragma omp parallel for shared(old_a) 
        for (int i = 0; i < LEN_1D; i++) {
            old_a[i] = a[i];
        }

        #pragma omp parallel for shared(old_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * old_a[i+1] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(old_a);
    return (real_t)0;
}
