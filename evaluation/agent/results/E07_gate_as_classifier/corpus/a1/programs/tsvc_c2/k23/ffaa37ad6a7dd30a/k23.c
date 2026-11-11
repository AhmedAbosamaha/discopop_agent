#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t prod_u = w[i] * c[i];
            real_t prod_v = x[i] * d[i] + c[i];
            u[i] += prod_u;
            v[i] = prod_v;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
