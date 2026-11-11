#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t w_i = w[i];
            real_t c_i = c[i];
            real_t x_i = x[i];
            real_t d_i = d[i];
            u[i] += w_i * c_i;
            v[i] = x_i * d_i + c_i;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
