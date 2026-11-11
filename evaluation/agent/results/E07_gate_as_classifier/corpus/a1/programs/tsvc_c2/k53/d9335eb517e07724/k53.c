#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t c_local[LEN_1D];
        for (long i = 1; i < LEN_1D; i++) {
            c_local[i] = c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c_local[i];
            v[jv[i]] = u[ku[i]] * d[i] + c_local[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
