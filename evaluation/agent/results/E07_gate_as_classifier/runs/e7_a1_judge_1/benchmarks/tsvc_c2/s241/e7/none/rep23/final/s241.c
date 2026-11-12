#include "data.h"

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = LEN_1D-2; i >= 0; i--) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
