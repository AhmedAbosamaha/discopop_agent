#include "data.h"

real_t kernel_k53(void)
{
    real_t *u_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *v_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(u_new, u, LEN_1D * sizeof(real_t));
        memcpy(v_new, v, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_new[ju[i]] += v[kv[i]] * c[i];
            v_new[jv[i]] = u_new[ku[i]] * d[i] + c[i];
        }

        memcpy(u, u_new, LEN_1D * sizeof(real_t));
        memcpy(v, v_new, LEN_1D * sizeof(real_t));

        dummy(a, b, c, d, e);
    }

    free(u_new);
    free(v_new);
    return (real_t)0;
}
