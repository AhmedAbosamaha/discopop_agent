#include "data.h"

real_t kernel_s292(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = i - 1;
            if (im1 < 0) im1 += LEN_1D;
            int im2 = i - 2;
            if (im2 < 0) im2 += LEN_1D;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        long k = (nl * 7919L + 13L) % LEN_1D;
        a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
        d[k] += (real_t)0.125; e[k] += (real_t)0.25;
        a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
    }
    return (real_t)0;
}
