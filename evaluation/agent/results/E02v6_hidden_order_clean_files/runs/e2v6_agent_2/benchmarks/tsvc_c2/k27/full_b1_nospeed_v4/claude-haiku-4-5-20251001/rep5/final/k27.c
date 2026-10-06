#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
