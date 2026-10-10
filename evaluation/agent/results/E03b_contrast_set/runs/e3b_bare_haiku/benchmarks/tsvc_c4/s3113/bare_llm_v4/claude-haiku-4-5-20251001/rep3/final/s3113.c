#include "data.h"

real_t kernel_s3113(void)
{
    real_t max;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for reduction(max:max)
        for (int i = 0; i < LEN_1D; i++) {
            if ((ABS(a[i])) > max) {
                max = ABS(a[i]);
            }
        }
        dummy(a, b, c, d, e, max);
    }
    return max;
}
