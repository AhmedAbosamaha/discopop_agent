#include "data.h"

real_t kernel_s292(void)
{
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        int im1 = (i - 1 + LEN_1D) % LEN_1D;
        int im2 = (i - 2 + LEN_1D) % LEN_1D;
        a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
    }
    return (real_t)0;
}
