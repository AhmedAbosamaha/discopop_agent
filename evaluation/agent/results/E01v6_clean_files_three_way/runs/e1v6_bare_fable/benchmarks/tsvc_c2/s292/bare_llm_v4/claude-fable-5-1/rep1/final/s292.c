#include "data.h"

real_t kernel_s292(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* im1/im2 are wrapped induction variables: im1 = (i-1) mod LEN_1D,
           im2 = (i-2) mod LEN_1D.  Closed form makes iterations independent. */
#pragma omp parallel for default(none) shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? (LEN_1D - 1) : (i - 1);
            int im2 = (i < 2) ? (LEN_1D - 2 + i) : (i - 2);
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
