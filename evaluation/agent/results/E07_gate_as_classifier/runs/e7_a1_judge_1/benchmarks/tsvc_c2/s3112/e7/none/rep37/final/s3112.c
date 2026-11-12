#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        // Parallel prefix sum using doubling algorithm
        // Copy a to b in parallel (no dependencies)
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i];
        }

        // Doubling stride: each pass computes new values from previous stride
        // Use temp array to make independence explicit to the profiler
        real_t *temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int stride = 1; stride < LEN_1D; stride *= 2) {
            // Read from b, write to temp (parallelizable: no loop-carried deps)
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

        // Final sum is the last element of the cumulative array
        sum = b[LEN_1D - 1];
        dummy(a, b, c, d, e);
    }
    return sum;
}
