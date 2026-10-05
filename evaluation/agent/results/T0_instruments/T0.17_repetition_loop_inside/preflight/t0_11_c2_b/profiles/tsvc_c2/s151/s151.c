#include "data.h"

void s151s(real_t a[LEN_1D], real_t b[LEN_1D],  int m)
{
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] = a[i + m] + b[i];
    }
}

real_t kernel_s151(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        s151s(a, b,  1);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
