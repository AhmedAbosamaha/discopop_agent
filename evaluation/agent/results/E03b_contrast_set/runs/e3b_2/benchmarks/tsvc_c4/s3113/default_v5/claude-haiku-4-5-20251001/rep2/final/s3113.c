#include "data.h"

real_t kernel_s3113(void)
{
    real_t max;
    for (int nl = 0; nl < iterations; nl++) {
        max = ABS(a[0]);
        #pragma omp parallel for reduction(max:max) 
        for (int i = 1; i < LEN_1D; i++) {
            real_t val = ABS(a[i]);
            max = fmax(max, val);
        }
        dummy(a, b, c, d, e, max);
    }
    return max;
}
