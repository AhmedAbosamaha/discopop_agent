#include "data.h"

real_t kernel_s131(void)
{
    int m  = 1;
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i] = a[i + m] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
