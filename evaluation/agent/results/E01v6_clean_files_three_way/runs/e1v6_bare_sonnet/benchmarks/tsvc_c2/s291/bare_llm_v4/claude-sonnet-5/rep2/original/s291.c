#include "data.h"

real_t kernel_s291(void)
{
    int im1;
    for (int nl = 0; nl < iterations; nl++) {
        im1 = LEN_1D-1;
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = (b[i] + b[im1]) * (real_t).5;
            im1 = i;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
