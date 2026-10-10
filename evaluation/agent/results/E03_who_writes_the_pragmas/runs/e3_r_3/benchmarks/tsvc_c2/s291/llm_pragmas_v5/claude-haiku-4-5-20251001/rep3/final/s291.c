#include "data.h"

real_t kernel_s291(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i == 0 ? LEN_1D - 1 : i - 1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
