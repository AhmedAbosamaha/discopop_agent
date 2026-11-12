#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            long iu = ju[i];
            long iv = kv[i];
            u[iu] += v[iv] * c[i];
            long jv_idx = jv[i];
            long iu2 = ku[i];
            v[jv_idx] = u[iu2] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
