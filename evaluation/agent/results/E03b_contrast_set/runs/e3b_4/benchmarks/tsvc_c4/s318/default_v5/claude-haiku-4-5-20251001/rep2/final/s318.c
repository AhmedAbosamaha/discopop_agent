#include "data.h"
#include <stdlib.h>

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute absolute values in parallel
        // No loop-carried dependencies: each iteration writes to a different array element
        real_t *abs_vals = (real_t *)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(abs_vals) 
        for (int i = 0; i < LEN_1D; i++) {
            abs_vals[i] = ABS(a[i * inc]);
        }

        // Phase 2: Find maximum value and its index (sequential reduction)
        index = 0;
        max = abs_vals[0];
        for (int i = 1; i < LEN_1D; i++) {
            if (abs_vals[i] > max) {
                max = abs_vals[i];
                index = i;
            }
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
        free(abs_vals);
    }
    return max + index + 1;
}
