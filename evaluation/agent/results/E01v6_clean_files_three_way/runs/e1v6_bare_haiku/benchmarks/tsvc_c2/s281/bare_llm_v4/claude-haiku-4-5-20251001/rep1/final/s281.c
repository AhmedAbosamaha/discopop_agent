#include "data.h"
#include <stdlib.h>

real_t kernel_s281(void)
{
    real_t x;
    real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy array a to capture initial state before modifications
        #pragma omp parallel for shared(a, a_copy)
        for (int i = 0; i < LEN_1D; i++) {
            a_copy[i] = a[i];
        }

        // Main computation loop: read from snapshot, write to independent locations
        #pragma omp parallel for private(x) shared(a, b, c, a_copy)
        for (int i = 0; i < LEN_1D; i++) {
            x = a_copy[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        dummy(a, b, c, d, e);
    }

    free(a_copy);
    return (real_t)0;
}
