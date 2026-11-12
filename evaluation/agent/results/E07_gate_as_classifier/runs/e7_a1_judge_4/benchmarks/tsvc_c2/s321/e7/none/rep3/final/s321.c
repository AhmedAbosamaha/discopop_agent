#include "data.h"

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            c[i] = a[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            c[i] += c[i-1] * b[i];
        }
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
