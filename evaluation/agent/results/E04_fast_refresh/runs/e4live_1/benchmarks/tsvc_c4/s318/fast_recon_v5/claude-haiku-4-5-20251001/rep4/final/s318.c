#include "data.h"
#include <stdlib.h>

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;

    // Allocate array for computed absolute values (reused across outer loop)
    real_t *candidates = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute absolute values for all array elements.
        // No loop-carried dependences; each iteration computes a distinct element.
        #pragma omp parallel for shared(candidates) 
        for (int i = 0; i < LEN_1D; i++) {
            candidates[i] = ABS(a[i * inc]);
        }

        // Phase 2: Find the maximum value and its index from pre-computed candidates.
        // Sequential phase operating on already-computed data.
        max = candidates[0];
        index = 0;
        for (int i = 1; i < LEN_1D; i++) {
            if (candidates[i] > max) {
                max = candidates[i];
                index = i;
            }
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }

    free(candidates);
    return max + index + 1;
}
