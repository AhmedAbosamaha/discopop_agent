#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t u_delta = w[kw[i]] * c[i];
            u[ju[i]] += u_delta;
            real_t v_val = u[ku[i]] * d[i] + c[i];
            v[jv[i]] = v_val;
            real_t w_val = v[kv[i]] * e[i] + d[i];
            w[jw[i]] = w_val;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
