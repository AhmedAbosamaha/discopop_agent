#include "data.h"

real_t kernel_s3113(void)
{
    real_t max;
    for (int nl = 0; nl < iterations; nl++) {
        real_t local_max;
        #pragma omp parallel for reduction(max:local_max)
        for (int i = 0; i < LEN_1D; i++) {
            if ((ABS(a[i])) > local_max) {
                local_max = ABS(a[i]);
            }
        }
        max = local_max;
        dummy(a, b, c, d, e, max);
    }
    return max;
}
