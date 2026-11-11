#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t u_contrib = w[kw[i]] * c[i];
            real_t v_val = u[ku[i]] * d[i] + c[i];
            real_t w_val = v[kv[i]] * e[i] + d[i];
            u[ju[i]] += u_contrib;
            v[jv[i]] = v_val;
            w[jw[i]] = w_val;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
