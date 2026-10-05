#include "data.h"

real_t kernel_s254(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        x = b[LEN_1D-1];
        a[0] = (b[0] + x) * (real_t).5;
        #pragma omp parallel for schedule(static) default(none) shared(a, b)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
