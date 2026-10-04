#include "data.h"

real_t kernel_s252(void)
{
    real_t t, s;
    t = (real_t) 0.;
    for (int i = 0; i < LEN_1D; i++) {
        s = b[i] * c[i];
        a[i] = s + t;
        t = s;
    }
    return (real_t)0;
}
