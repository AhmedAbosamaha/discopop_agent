#include "data.h"

real_t kernel_s291(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* i == 0 uses im1 = LEN_1D-1 (wrap-around); peeled out */
        a[0] = (b[0] + b[LEN_1D-1]) * (real_t).5;
        /* for i >= 1, im1 == i-1; only b is read, a is written: independent */
#pragma omp parallel for schedule(static) default(none) shared(a, b)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
