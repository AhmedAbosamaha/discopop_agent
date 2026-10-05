#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            int prev = (i - 1 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[prev]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
