#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* x carried b[i-1] into iteration i; i == 0 used the wrap-around
           value b[LEN_1D-1].  Read the predecessor directly instead. */
        a[0] = (b[0] + b[LEN_1D-1]) * (real_t).5;
#pragma omp parallel for default(none) shared(a, b)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
