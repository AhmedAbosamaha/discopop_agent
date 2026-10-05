#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    int *indices = (int *)malloc(LEN_1D * sizeof(int));

    // Compute prefix sum once (b is constant across all nl iterations)
    int idx = 0;
    for (int i = 0; i < LEN_1D; i++) {
        if (b[i] > (real_t)0.) {
            indices[i] = idx;
            idx++;
        }
    }
    j = idx - 1;

    for (int nl = 0; nl < iterations; nl++) {
        // Write filtered elements to array a using precomputed indices
        #pragma omp parallel for shared(indices) 
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[indices[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(indices);
    return (real_t)0;
}
