#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int x_idx = (i - 1 + LEN_1D) % LEN_1D;
            int y_idx = (i - 2 + LEN_1D) % LEN_1D;
            real_t x = b[x_idx];
            real_t y = b[y_idx];
            a[i] = (b[i] + x + y) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
