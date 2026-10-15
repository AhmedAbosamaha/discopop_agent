#include "data.h"

real_t kernel_s254(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            if (i == 0) {
                a[i] = (b[i] + b[LEN_1D-1]) * (real_t).5;
            } else {
                a[i] = (b[i] + b[i-1]) * (real_t).5;
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
