#include "data.h"

real_t kernel_s292(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            int im1_local = (i - 1 + LEN_1D) % LEN_1D;
            int im2_local = (i - 2 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[im1_local] + b[im2_local]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
