#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_orig = malloc(LEN_1D * sizeof(real_t));
        memcpy(u_orig, u, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u_orig[ku[i]] * d[i] + c[i];
        }

        free(u_orig);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
