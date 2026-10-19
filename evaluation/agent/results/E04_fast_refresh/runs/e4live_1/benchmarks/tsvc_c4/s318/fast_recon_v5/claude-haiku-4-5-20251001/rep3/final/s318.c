#include "data.h"
#include <stdlib.h>

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: extract all absolute values into temporary array (Do-All)
        real_t *values = (real_t *)malloc(LEN_1D * sizeof(real_t));
        values[0] = ABS(a[0]);
        #pragma omp parallel for shared(values) 
        for (int i = 1; i < LEN_1D; i++) {
            int k = i * inc;
            values[i] = ABS(a[k]);
        }

        // Second pass: find maximum and its index (sequential, outside parallelizable region)
        max = values[0];
        index = 0;
        for (int i = 1; i < LEN_1D; i++) {
            if (values[i] > max) {
                index = i;
                max = values[i];
            }
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
        free(values);
    }
    return max + index + 1;
}
