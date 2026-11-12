#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i];
        }
        real_t suffix = 0.0;
        for (int i = LEN_1D - 1; i >= 0; i--) {
            suffix += a[i];
            b[i] = sum - suffix + a[i];
        }
        dummy(a, b, c, d, e);
    }
    return sum;
}
