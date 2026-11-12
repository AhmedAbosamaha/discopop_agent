#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    int *indices = malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        j = -1;

        // Pass 1: Compute write indices for each element
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                j++;
            }
            indices[i] = j;
        }

        // Pass 2: Place filtered elements in parallel
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
