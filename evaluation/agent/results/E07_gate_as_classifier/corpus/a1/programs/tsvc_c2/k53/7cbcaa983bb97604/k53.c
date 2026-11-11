#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *delta_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *delta_v = (real_t *)malloc(LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            delta_u[i] = v[kv[i]] * c[i];
            delta_v[i] = u[ku[i]] * d[i] + c[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += delta_u[i];
            v[jv[i]] = delta_v[i];
        }

        free(delta_u);
        free(delta_v);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
