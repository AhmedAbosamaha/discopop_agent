#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t u_inc[LEN_1D];
        for (long j = 0; j < LEN_1D; j++) u_inc[j] = 0.0;

        for (long i = 1; i < LEN_1D; i++) {
            u_inc[ju[i]] += v[kv[i]] * c[i];
        }

        for (long j = 0; j < LEN_1D; j++) {
            u[j] += u_inc[j];
        }

        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
