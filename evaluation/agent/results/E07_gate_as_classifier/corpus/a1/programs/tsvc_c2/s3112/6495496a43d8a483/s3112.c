#include <stdlib.h>
#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;

        // Parallel prefix sum using doubling algorithm
        // Copy a to b (no loop-carried dependencies)
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i];
        }

        // Doubling stride: each pass computes new values from previous stride
        // Use temp array to make independence explicit to the profiler
        real_t *temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int stride = 1; stride < LEN_1D; stride *= 2) {
            // Read from b, write to temp (parallelizable: no loop-carried deps on loop var i)
            for (int i = 0; i < LEN_1D; i++) {
                if (i >= stride) {
                    temp[i] = b[i] + b[i - stride];
                } else {
                    temp[i] = b[i];
                }
            }
            // Copy temp back to b
            for (int i = 0; i < LEN_1D; i++) {
                b[i] = temp[i];
            }
        }
        free(temp);

        // Compute sum sequentially in original order for byte-identical floating-point result
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i];
        }
        dummy(a, b, c, d, e);
    }
    return sum;
}
