#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            real_t u_val = u[ku[i]];
            v[jv[i]] = u_val * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
