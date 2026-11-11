#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        real_t new_a[LEN_1D];
        for (int i = 0; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            new_a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = new_a[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
