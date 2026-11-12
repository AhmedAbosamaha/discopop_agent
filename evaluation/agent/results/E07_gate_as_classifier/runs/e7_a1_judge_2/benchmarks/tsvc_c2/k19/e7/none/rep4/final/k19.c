#include "data.h"

real_t kernel_k19(void)
{
    real_t *u_contrib = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memset(u_contrib, 0, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_contrib[ju[i]] += v[kv[i]] * c[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += u_contrib[ju[i]];
        }

        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        dummy(a, b, c, d, e);
    }

    free(u_contrib);
    return (real_t)0;
}
