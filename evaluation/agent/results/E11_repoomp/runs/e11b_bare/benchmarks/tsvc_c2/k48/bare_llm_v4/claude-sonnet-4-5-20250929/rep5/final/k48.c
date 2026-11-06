#include "data.h"

real_t kernel_k48(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(u, v, c, ju, kv)
        for (long i = 1; i < LEN_1D; i++) {
            #pragma omp atomic
            u[ju[i]] += v[kv[i]] * c[i];
        }
        #pragma omp parallel for shared(v, u, d, c, jv, ku)
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
