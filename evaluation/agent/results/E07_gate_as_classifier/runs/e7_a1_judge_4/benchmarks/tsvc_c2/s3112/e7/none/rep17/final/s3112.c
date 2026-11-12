#include "data.h"
#include <stdlib.h>

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        real_t* prefix_sum = (real_t*)malloc(LEN_1D * sizeof(real_t));
        real_t temp_sum = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            temp_sum += a[i];
            prefix_sum[i] = temp_sum;
        }
        sum = temp_sum;
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = prefix_sum[i];
        }
        dummy(a, b, c, d, e);
        free(prefix_sum);
    }
    return sum;
}
