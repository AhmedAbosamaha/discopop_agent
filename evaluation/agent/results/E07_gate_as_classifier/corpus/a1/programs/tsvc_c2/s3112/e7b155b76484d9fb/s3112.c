#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    for (int nl = 0; nl < iterations; nl++) {
        real_t local_sum = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            local_sum += a[i];
            b[i] = local_sum;
        }
        sum = local_sum;
        dummy(a, b, c, d, e);
    }
    return sum;
}
