#include "data.h"

real_t kernel_k17(void)
{
    #pragma omp parallel for 
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] += u[ku[i]] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
