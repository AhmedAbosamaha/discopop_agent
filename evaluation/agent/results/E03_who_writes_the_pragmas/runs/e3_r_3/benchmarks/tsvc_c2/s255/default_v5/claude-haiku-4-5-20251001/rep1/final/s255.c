#include "data.h"

real_t kernel_s255(void)
{
    real_t x, y;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int i_prev_1 = (i - 1 + LEN_1D) % LEN_1D;
            int i_prev_2 = (i - 2 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[i_prev_1] + b[i_prev_2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
