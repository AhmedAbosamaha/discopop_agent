#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int prev_i = (i - 1 + LEN_1D) % LEN_1D;
            int prev_prev_i = (i - 2 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[prev_i] + b[prev_prev_i]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
