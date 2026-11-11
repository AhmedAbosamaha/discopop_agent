#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    int *counts = (int *)malloc(iterations * sizeof(int));
    int *offsets = (int *)malloc(iterations * sizeof(int));

    /* Count positive elements per outer iteration (parallelizable) */
    for (int nl = 0; nl < iterations; nl++) {
        counts[nl] = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                counts[nl]++;
            }
        }
    }

    /* Compute write offsets for each outer iteration (serial, small) */
    offsets[0] = 0;
    for (int nl = 1; nl < iterations; nl++) {
        offsets[nl] = offsets[nl-1] + counts[nl-1];
    }

    /* Each outer iteration writes to its assigned region of a (outer loop parallelizable) */
    for (int nl = 0; nl < iterations; nl++) {
        j = offsets[nl];
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[j] = b[i];
                j++;
            }
        }
        dummy(a, b, c, d, e);
    }

    free(counts);
    free(offsets);
    return (real_t)0;
}
