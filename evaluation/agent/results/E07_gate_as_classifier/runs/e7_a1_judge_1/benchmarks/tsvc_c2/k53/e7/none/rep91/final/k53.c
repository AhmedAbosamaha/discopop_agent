#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t u_ku_i = u[ku[i]];
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u_ku_i * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
