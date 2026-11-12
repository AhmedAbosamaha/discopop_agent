#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        // Initialize b with values from a
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i];
        }
        // Cascade: each element becomes cumulative sum
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D; i++) {
            b[i] += b[i-1];
        }
        sum = b[LEN_1D - 1];
        dummy(a, b, c, d, e);
    }
    return sum;
}
