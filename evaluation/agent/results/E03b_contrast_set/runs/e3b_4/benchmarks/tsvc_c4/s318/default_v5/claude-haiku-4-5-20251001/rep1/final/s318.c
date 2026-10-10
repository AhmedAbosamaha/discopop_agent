#include <stdlib.h>
#include "data.h"

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        real_t *vals = (real_t *)malloc(LEN_1D * sizeof(real_t));

        // First pass: compute absolute values (Do-All, no dependences)
        #pragma omp parallel for shared(vals) 
        for (int i = 0; i < LEN_1D; i++) {
            vals[i] = ABS(a[i * inc]);
        }

        // Second pass: find max and index (sequential reduction)
        index = 0;
        max = vals[0];
        for (int i = 1; i < LEN_1D; i++) {
            if (vals[i] > max) {
                max = vals[i];
                index = i;
            }
        }

        free(vals);

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
