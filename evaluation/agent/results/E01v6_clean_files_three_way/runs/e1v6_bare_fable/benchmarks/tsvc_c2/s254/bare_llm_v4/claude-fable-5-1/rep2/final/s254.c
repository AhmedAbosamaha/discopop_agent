#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* x in iteration i is b[i-1]; for i == 0 it is b[LEN_1D-1].
           b is not written inside the i loop, so read it directly. */
        a[0] = (b[0] + b[LEN_1D-1]) * (real_t).5;
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
