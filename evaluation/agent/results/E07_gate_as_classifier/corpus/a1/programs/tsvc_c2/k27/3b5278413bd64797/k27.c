#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            long j_u = ju[i];
            long k_u = ku[i];
            long j_v = jv[i];
            long k_v = kv[i];
            long j_w = jw[i];
            long k_w = kw[i];
            u[j_u] += w[k_w] * c[i];
            v[j_v] = u[k_u] * d[i] + c[i];
            w[j_w] = v[k_v] * e[i] + d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
