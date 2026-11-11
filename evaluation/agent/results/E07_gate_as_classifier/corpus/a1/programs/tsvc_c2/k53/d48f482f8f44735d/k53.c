#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        long i = 1;
        u[ju[i]] += v[kv[i]] * c[i];
        for (i = 2; i < LEN_1D; i++) {
            v[jv[i-1]] = u[ku[i-1]] * d[i-1] + c[i-1];
            u[ju[i]] += v[kv[i]] * c[i];
        }
        v[jv[LEN_1D-1]] = u[ku[LEN_1D-1]] * d[LEN_1D-1] + c[LEN_1D-1];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
