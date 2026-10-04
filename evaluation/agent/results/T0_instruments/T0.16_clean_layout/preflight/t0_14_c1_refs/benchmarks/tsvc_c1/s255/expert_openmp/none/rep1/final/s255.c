#include "data.h"

real_t kernel_s255(void)
{
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) {
        real_t x = b[(i + LEN_1D - 1) % LEN_1D];
        real_t y = b[(i + LEN_1D - 2) % LEN_1D];
        a[i] = (b[i] + x + y) * (real_t).333;
    }
    return (real_t)0;
}
