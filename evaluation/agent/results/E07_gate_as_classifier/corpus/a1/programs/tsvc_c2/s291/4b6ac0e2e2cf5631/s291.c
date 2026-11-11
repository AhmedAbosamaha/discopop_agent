#include "data.h"

real_t kernel_s291(void)
{
    int im1;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int prev = (i == 0) ? (LEN_1D - 1) : (i - 1);
            a[i] = (b[i] + b[prev]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
