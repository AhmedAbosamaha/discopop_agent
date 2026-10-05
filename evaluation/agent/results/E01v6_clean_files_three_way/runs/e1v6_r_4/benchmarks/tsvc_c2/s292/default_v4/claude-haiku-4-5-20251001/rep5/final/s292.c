#include "data.h"

real_t kernel_s292(void)
{
    int im1, im2;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(im1,im2) 
        for (int i = 0; i < LEN_1D; i++) {
            im1 = (i - 1 + LEN_1D) % LEN_1D;
            im2 = (i - 2 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
