#include "data.h"

real_t kernel_s292(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int im1, im2;
            if (i == 0) {
                im1 = LEN_1D - 1;
                im2 = LEN_1D - 2;
            } else if (i == 1) {
                im1 = 0;
                im2 = LEN_1D - 1;
            } else {
                im1 = i - 1;
                im2 = i - 2;
            }
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
