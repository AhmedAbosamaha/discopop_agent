#include "data.h"

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t a_saved[LEN_1D];
        for (int i = 0; i < LEN_1D; i++) {
            a_saved[i] = a[i];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a_saved[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
