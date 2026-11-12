#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t w_val = w[i];
            real_t c_val = c[i];
            real_t x_val = x[i];
            real_t d_val = d[i];
            u[i] += w_val * c_val;
            v[i] = x_val * d_val + c_val;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
