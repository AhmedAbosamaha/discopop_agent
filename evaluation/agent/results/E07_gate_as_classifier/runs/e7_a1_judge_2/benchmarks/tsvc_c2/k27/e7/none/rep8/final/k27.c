#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            if (i > 1) {
                w[jw[i-1]] = v[kv[i-1]] * e[i-1] + d[i-1];
            }
            u[ju[i]] += w[kw[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        w[jw[LEN_1D-1]] = v[kv[LEN_1D-1]] * e[LEN_1D-1] + d[LEN_1D-1];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
