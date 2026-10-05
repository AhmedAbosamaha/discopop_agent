#include "data.h"

real_t kernel_s292(void)
{
    for (int nl = 0; nl < iterations; nl++) {
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            /* wrap-around indices: i-1 and i-2 modulo LEN_1D */
            int im1 = (i == 0) ? (LEN_1D - 1) : (i - 1);
            int im2 = (i < 2) ? (i + LEN_1D - 2) : (i - 2);
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
