#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    // Allocate local buffer to hold current iteration's a values for next iteration's reads
    real_t *a_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
    if (!a_prev) {
        return (real_t)0;
    }

    // Initialize a_prev with the input array a
    #pragma omp parallel for shared(a_prev) 
    for (int i = 0; i < LEN_1D; i++) {
        a_prev[i] = a[i];
    }

    for (int nl = 0; nl < iterations; nl++) {
        if (nl > 0) {
            dummy(a, b, c, d, e);
            // Save a after dummy() modifies it, for this iteration's first loop
            #pragma omp parallel for shared(a_prev) 
            for (int i = 0; i < LEN_1D; i++) {
                a_prev[i] = a[i];
            }
        }
        // Read from a_prev (which is either the initial a or a after dummy() modified it)
        #pragma omp parallel for shared(a_prev) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a_prev[i + 1] * d[i];
        }
        // Modify a for next iteration
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
    }

    free(a_prev);

    if (iterations > 0) {
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
