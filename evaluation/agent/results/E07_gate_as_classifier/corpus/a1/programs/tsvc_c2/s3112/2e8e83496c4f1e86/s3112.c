#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            b[i] += b[i-1];
        }
        if (LEN_1D > 0) {
            sum = b[LEN_1D - 1];
        }
        dummy(a, b, c, d, e);
    }
    return sum;
}
