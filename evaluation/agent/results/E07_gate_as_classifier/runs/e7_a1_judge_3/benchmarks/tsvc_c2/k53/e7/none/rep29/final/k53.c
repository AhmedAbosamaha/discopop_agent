#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_new = malloc(sizeof(real_t) * LEN_1D);
        real_t *v_new = malloc(sizeof(real_t) * LEN_1D);
        memcpy(u_new, u, sizeof(real_t) * LEN_1D);
        memcpy(v_new, v, sizeof(real_t) * LEN_1D);

        for (long i = 1; i < LEN_1D; i++) {
            u_new[ju[i]] += v_new[kv[i]] * c[i];
            v_new[jv[i]] = u_new[ku[i]] * d[i] + c[i];
        }

        memcpy(u, u_new, sizeof(real_t) * LEN_1D);
        memcpy(v, v_new, sizeof(real_t) * LEN_1D);

        free(u_new);
        free(v_new);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
