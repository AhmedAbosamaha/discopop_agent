#include "data.h"

real_t kernel_s292(void)
{
    int im1, im2;
    for (int nl = 0; nl < iterations; nl++) {
        im1 = LEN_1D-1;
        im2 = LEN_1D-2;
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int idx1 = (i == 0) ? (LEN_1D-1) : (i-1);
            int idx2 = (i == 0) ? (LEN_1D-2) : ((i == 1) ? (LEN_1D-1) : (i-2));
            a[i] = (b[i] + b[idx1] + b[idx2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
