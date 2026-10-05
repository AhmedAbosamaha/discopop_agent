#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static) \
            shared(a, b) private(i)
        for (int i = 0; i < LEN_1D; i++) {
            int i_prev = (i - 1 + LEN_1D) % LEN_1D;
            int i_prev2 = (i - 2 + LEN_1D) % LEN_1D;
            real_t x = b[i_prev];
            real_t y = b[i_prev2];
            a[i] = (b[i] + x + y) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
