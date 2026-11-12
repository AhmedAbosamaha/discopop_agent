#include <stdlib.h>
#include "data.h"

real_t kernel_s341(void)
{
    int* indices = (int*)malloc(LEN_1D * sizeof(int));
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: compute output indices for elements that pass the filter
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                indices[i] = count;
                count++;
            }
        }
        // Second pass: write filtered elements to their computed positions
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
