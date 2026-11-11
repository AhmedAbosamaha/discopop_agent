#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t v_val = v[kv[i]];
            real_t u_val = u[ku[i]];
            u[ju[i]] += v_val * c[i];
            v[jv[i]] = u_val * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
