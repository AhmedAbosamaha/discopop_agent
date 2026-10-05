#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        {
            real_t s0 = b[0] * c[0];
            real_t t0 = (real_t) 0.;
            a[0] = s0 + t0;
        }
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c)
        for (int i = 1; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t t = b[i-1] * c[i-1];
            a[i] = s + t;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
