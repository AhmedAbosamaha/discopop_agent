#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t tmp_w = w[kw[i]] * c[i];
            u[ju[i]] += tmp_w;
            real_t tmp_u = u[ku[i]] * d[i] + c[i];
            v[jv[i]] = tmp_u;
            real_t tmp_v = v[kv[i]] * e[i] + d[i];
            w[jw[i]] = tmp_v;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
