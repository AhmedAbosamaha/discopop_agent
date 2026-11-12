#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t u_term = w[kw[i]] * c[i];
            u[ju[i]] += u_term;
            real_t v_term = u[ku[i]] * d[i] + c[i];
            v[jv[i]] = v_term;
            real_t w_term = v[kv[i]] * e[i] + d[i];
            w[jw[i]] = w_term;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
