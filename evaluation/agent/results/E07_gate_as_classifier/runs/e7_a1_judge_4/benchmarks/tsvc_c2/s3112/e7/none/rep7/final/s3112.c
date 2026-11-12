#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        real_t sum_prev = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            real_t sum = sum_prev + a[i];
            b[i] = sum;
            sum_prev = sum;
        }
        sum = sum_prev;
        dummy(a, b, c, d, e);
    }
    return sum;
}
