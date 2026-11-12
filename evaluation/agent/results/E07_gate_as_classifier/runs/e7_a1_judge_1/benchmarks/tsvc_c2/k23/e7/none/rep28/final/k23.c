#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t temp_u[LEN_1D];
        for (long i = 1; i < LEN_1D; i++) {
            temp_u[i] = w[i] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = x[i] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += temp_u[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
