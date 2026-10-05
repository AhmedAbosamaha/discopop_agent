#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    // Static allocation: allocate once, outside the repeated loop
    static real_t *a_copy = NULL;
    if (a_copy == NULL) {
        a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));
    }

    // Preserve original values of a before modification
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        a_copy[i] = a[i];
    }

    // Phase 1: update a[i] values (Do-All loop)
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] *= c[i];
    }

    // Phase 2: compute b[i] using original a values (Do-All loop)
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D-1; i++) {
        b[i] += a_copy[i + 1] * d[i];
    }

    return (real_t)0;
}
