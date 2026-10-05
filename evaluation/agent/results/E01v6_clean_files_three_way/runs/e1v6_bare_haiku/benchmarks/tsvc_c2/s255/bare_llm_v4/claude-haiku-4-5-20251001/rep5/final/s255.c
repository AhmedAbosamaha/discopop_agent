#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = (b[i] + b[(i-1+LEN_1D)%LEN_1D] + b[(i-2+LEN_1D)%LEN_1D]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
