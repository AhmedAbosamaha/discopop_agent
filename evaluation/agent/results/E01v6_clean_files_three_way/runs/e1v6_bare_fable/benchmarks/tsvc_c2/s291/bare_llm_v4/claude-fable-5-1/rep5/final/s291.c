#include "data.h"

real_t kernel_s291(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* im1 was a carried induction variable: im1 == (i == 0 ? LEN_1D-1 : i-1).
           Computed per-iteration so the loop carries no dependence. */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? (LEN_1D - 1) : (i - 1);
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
