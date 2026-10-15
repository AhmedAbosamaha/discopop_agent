#include "data.h"
#include <stdlib.h>

real_t kernel_s281(void)
{
    real_t x;
    int boundary = (LEN_1D - 1) / 2;
    real_t *a_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));

    // Initialize a_prev with starting values
    #pragma omp parallel for shared(a_prev) 
    for (int i = 0; i < LEN_1D; i++) {
        a_prev[i] = a[i];
    }

    for (int nl = 0; nl < iterations; nl++) {
        // Stage 1: read from a_prev (stable), write to a
        #pragma omp parallel for firstprivate(boundary) private(x) shared(a_prev) 
        for (int i = 0; i <= boundary; i++) {
            x = a_prev[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        // Stage 2: read from updated a (stage 1 writes), write to a
        #pragma omp parallel for firstprivate(boundary) private(x) 
        for (int i = boundary + 1; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        // Update a_prev with current a for next iteration
        #pragma omp parallel for shared(a_prev) 
        for (int i = 0; i < LEN_1D; i++) {
            a_prev[i] = a[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_prev);
    return (real_t)0;
}
