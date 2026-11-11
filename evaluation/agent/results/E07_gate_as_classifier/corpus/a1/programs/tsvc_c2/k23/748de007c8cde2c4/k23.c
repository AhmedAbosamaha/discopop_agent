#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D - 1; i++) {
            u[i+1] = u[i+1] + w[i+1] * c[i+1];
        }
        for (long i = 0; i < LEN_1D - 1; i++) {
            v[i+1] = x[i+1] * d[i+1] + c[i+1];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
