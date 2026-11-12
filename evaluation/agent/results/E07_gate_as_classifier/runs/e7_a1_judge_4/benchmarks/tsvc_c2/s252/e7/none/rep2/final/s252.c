#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            a[i] = s + t;
            t = s;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
