#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: compute output positions for elements that pass filter
        int *indices = (int *)malloc(LEN_1D * sizeof(int));
        int idx = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                indices[i] = idx;
                idx++;
            }
        }
        j = idx - 1;

        // Second pass: write filtered elements to array a using precomputed indices
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[indices[i]] = b[i];
            }
        }

        free(indices);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
