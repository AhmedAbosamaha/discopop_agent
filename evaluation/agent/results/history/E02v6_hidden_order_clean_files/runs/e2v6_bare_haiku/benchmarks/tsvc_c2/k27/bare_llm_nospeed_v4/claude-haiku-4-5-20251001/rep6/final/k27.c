#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(u, v, w, c, d, e, ju, jv, jw, ku, kv, kw)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
