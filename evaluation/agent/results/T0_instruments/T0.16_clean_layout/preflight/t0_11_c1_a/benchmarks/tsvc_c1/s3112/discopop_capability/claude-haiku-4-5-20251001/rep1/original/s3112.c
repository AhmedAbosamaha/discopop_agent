#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    sum = (real_t)0.0;
    for (int i = 0; i < LEN_1D; i++) {
        sum += a[i];
        b[i] = sum;
    }
    return sum;
}
