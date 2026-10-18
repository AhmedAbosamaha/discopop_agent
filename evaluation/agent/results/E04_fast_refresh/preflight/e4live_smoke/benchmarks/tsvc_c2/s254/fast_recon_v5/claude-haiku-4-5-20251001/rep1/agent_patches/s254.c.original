#include "data.h"

real_t kernel_s254(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        x = b[LEN_1D-1];
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = (b[i] + x) * (real_t).5;
            x = b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
