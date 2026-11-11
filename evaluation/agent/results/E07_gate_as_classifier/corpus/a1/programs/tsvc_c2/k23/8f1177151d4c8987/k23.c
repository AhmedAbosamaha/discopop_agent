#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t c_i = c[i];
            u[i] += w[i] * c_i;
            v[i] = x[i] * d[i] + c_i;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
