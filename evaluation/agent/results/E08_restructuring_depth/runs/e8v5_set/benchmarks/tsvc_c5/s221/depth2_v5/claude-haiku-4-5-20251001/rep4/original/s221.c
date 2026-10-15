#include "data.h"

real_t kernel_s221(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += c[i] * d[i];
            b[i] = b[i - 1] + a[i] + d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
