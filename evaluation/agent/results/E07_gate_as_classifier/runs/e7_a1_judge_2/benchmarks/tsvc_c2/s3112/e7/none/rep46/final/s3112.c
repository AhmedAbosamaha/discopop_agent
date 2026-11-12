#include <stdlib.h>
#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;

        // Stage 1: compute cumulative sums sequentially (preserves exact floating-point order)
        real_t *temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i];
            temp[i] = sum;
        }

        // Stage 2: copy cumulative sums to output (parallelizable: no loop-carried dependencies)
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = temp[i];
        }
        free(temp);
        dummy(a, b, c, d, e);
    }
    return sum;
}
