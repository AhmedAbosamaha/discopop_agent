#include "data.h"

real_t kernel_s292(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* im1 == (i-1) mod LEN_1D and im2 == (i-2) mod LEN_1D; computed
           directly so iterations are independent. */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i >= 1) ? i - 1 : LEN_1D - 1;
            int im2 = (i >= 2) ? i - 2 : LEN_1D - 2 + i;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
