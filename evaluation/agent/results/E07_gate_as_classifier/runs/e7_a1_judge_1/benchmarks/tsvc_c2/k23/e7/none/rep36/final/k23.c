#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t wi_ci = w[i] * c[i];
            u[i] += wi_ci;
            real_t xi_di = x[i] * d[i];
            v[i] = xi_di + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
