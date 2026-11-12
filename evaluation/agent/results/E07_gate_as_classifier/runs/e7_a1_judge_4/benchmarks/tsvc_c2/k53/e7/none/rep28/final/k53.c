#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t v_new[LEN_1D];
        for (long j = 0; j < LEN_1D; j++) v_new[j] = v[j];

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v_new[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        for (long j = 0; j < LEN_1D; j++) v[j] = v_new[j];

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
