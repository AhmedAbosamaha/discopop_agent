#include "data.h"
#include <stdlib.h>

real_t kernel_s315(void)
{
    real_t x, chksum;
    int index;

    // Allocate temporary arrays once, outside the repeated loop
    real_t *vals = (real_t *)malloc(LEN_1D * sizeof(real_t));
    int *indices = (int *)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        // Stage 1: Do-All pattern — each iteration independently copies value and index
        #pragma omp parallel for shared(vals,indices) 
        for (int i = 0; i < LEN_1D; ++i) {
            vals[i] = a[i];
            indices[i] = i;
        }

        // Stage 2: Reduction pattern — reduce arrays to find maximum
        x = vals[0];
        index = indices[0];
        for (int i = 1; i < LEN_1D; ++i) {
            if (vals[i] > x) {
                x = vals[i];
                index = indices[i];
            }
        }

        chksum = x + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }

    free(vals);
    free(indices);

    return index + x + 1;
}
