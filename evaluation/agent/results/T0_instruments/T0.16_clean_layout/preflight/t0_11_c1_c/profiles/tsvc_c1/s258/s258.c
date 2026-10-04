#include "data.h"

real_t kernel_s258(void)
{
    real_t s;
    s = 0.;
    for (int i = 0; i < LEN_2D; ++i) {
        if (a[i] > 0.) {
            s = d[i] * d[i];
        }
        b[i] = s * c[i] + d[i];
        e[i] = (s + (real_t)1.) * aa[0][i];
    }
    return (real_t)0;
}
