#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;

        // Pass 1: Compute total sum (reduction pattern)
        #pragma omp parallel for reduction(+:sum) 
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i];
        }

        // Pass 2: Compute prefix sums for array b
        real_t prefix_sum = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            prefix_sum += a[i];
            b[i] = prefix_sum;
        }

        dummy(a, b, c, d, e);
    }
    return sum;
}
