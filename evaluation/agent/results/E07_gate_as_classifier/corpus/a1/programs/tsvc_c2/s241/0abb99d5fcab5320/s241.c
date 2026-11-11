#include "data.h"

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t a_old[LEN_1D];
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
