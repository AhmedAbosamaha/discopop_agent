#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                goto L20;
            }
            a[i] = c[i] + d[i] * e[i];
            goto L10;
L20:
            c[i+1] = a[i] + d[i] * d[i];
L10:
            ;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
