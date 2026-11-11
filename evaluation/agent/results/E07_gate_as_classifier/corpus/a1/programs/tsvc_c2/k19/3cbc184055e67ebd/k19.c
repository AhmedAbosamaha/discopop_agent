#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            double v_temp = v[kv[i]];
            double u_temp = u[ku[i]];
            u[ju[i]] += v_temp * c[i];
            v[jv[i]] = u_temp * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
