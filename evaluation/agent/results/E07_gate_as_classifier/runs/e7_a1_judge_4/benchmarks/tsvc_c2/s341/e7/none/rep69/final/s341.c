#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;

        // Pass 1: Compute output indices for each element
        int *indices = malloc(LEN_1D * sizeof(int));
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                indices[i] = count++;
            }
        }

        // Pass 2: Write elements to their computed indices (Do-All)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[indices[i]] = b[i];
            }
        }

        j = count - 1;
        free(indices);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
