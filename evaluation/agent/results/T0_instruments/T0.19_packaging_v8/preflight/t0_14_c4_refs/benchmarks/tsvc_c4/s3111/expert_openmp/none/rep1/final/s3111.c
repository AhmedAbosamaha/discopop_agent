#include "data.h"

real_t kernel_s3111(void)
{
    real_t sum = 0;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.;
        #pragma omp parallel for reduction(+:sum)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] > (real_t)0.) {
                sum += a[i];
            }
        }
        dummy(a, b, c, d, e, sum);
    }
    return sum;
}
