#include "data.h"
#include <stdlib.h>

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;
    real_t *candidates = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Collect candidate values (Do-All—each iteration independent)
        #pragma omp parallel for shared(candidates) 
        for (int i = 0; i < LEN_1D; i++) {
            int k = i * inc;
            candidates[i] = ABS(a[k]);
        }

        // Phase 2: Find maximum and its index (sequential)
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
