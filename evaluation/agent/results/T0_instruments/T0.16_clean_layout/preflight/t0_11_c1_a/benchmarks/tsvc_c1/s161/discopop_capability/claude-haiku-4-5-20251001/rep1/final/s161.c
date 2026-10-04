#include "data.h"

real_t kernel_s161(void)
{
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
    return (real_t)0;
}
