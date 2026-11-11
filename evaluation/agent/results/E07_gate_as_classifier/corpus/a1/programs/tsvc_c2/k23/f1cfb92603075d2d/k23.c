#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t u_update = w[i] * c[i];
            u[i] = u[i] + u_update;
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
