#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        if (LEN_1D > 1) {
            a[1] = b[0] + c[1] * d[1];

            for (int i = 1; i < LEN_1D - 1; i++) {
                b[i] = a[i] + c[i] * e[i];
                a[i+1] = b[i] + c[i+1] * d[i+1];
            }

            b[LEN_1D-1] = a[LEN_1D-1] + c[LEN_1D-1] * e[LEN_1D-1];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
