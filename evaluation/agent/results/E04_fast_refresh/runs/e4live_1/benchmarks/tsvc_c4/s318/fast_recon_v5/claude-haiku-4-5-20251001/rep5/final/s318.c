#include "data.h"
#include <stdlib.h>

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute absolute values (parallelizable Do-All loop)
        // Allocate buffer to hold absolute values of all elements
        real_t* abs_vals = (real_t*) malloc(LEN_1D * sizeof(real_t));

        // Compute ABS(a[i*inc]) for each i, with no loop-carried dependencies
        #pragma omp parallel for shared(abs_vals) 
        for (int i = 0; i < LEN_1D; i++) {
            abs_vals[i] = ABS(a[i * inc]);
        }

        // Phase 2: Find maximum value and its index (sequential reduction)
        max = abs_vals[0];
        index = 0;
        for (int i = 1; i < LEN_1D; i++) {
            if (abs_vals[i] > max) {
                max = abs_vals[i];
                index = i;
            }
        }

        free(abs_vals);

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
