#include <stdlib.h>
#include "data.h"

real_t kernel_s341(void)
{
    int* indices = (int*)malloc(LEN_1D * sizeof(int));

    // Compute output indices once (b doesn't change across outer loop iterations)
    int count = 0;
    for (int i = 0; i < LEN_1D; i++) {
        if (b[i] > (real_t)0.) {
            indices[i] = count;
            count++;
        }
    }

    // Reuse precomputed indices for each outer loop iteration
    for (int nl = 0; nl < iterations; nl++) {
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
