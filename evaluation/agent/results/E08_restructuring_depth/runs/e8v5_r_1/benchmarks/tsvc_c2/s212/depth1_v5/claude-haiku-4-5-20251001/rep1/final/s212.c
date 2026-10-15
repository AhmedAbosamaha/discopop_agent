#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    real_t *a_saved = (real_t *)malloc(LEN_1D * sizeof(real_t));

    // Initialize a_saved with the initial state before entering the loop nest
    #pragma omp parallel for shared(a_saved) 
    for (int j = 0; j < LEN_1D; j++) {
        a_saved[j] = a[j];
    }

    for (int nl = 0; nl < iterations; nl++) {
        // Inner loop reads a[i+1] from the snapshot taken at the end of the previous iteration
        #pragma omp parallel for shared(a_saved) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
            b[i] += a_saved[i + 1] * d[i];
        }
        dummy(a, b, c, d, e);

        // Save current state of a after the inner loop modifies it
        #pragma omp parallel for shared(a_saved) 
        for (int j = 0; j < LEN_1D; j++) {
            a_saved[j] = a[j];
        }
    }

    free(a_saved);
    return (real_t)0;
}
