#include "data.h"

real_t kernel_s277(void)
{
    for (int i = 0; i < LEN_1D-1; i++) {
            if (a[i] >= (real_t)0.) {
                goto L20;
            }
            if (b[i] >= (real_t)0.) {
                goto L30;
            }
            a[i] += c[i] * d[i];
L30:
            b[i+1] = c[i] + d[i] * e[i];
L20:
;
    }
    return (real_t)0;
}
