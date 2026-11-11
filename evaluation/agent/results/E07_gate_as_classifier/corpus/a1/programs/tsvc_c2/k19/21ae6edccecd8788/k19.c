#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t u_inc = v[kv[i]] * c[i];
            real_t v_new = u[ku[i]] * d[i] + c[i];
            u[ju[i]] += u_inc;
            v[jv[i]] = v_new;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
