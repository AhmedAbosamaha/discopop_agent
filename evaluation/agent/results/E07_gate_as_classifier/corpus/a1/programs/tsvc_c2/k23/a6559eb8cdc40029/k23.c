#include "data.h"

real_t kernel_k23(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        for (int nl = 0; nl < iterations; nl++) {
            u[i] += w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
    }
    for (int nl = 0; nl < iterations; nl++) {
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
