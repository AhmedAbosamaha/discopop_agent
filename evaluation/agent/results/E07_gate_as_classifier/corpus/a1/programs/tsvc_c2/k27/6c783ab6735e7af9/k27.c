#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_temp = malloc(LEN_1D * sizeof(real_t));
        real_t *v_temp = malloc(LEN_1D * sizeof(real_t));
        memcpy(u_temp, u, LEN_1D * sizeof(real_t));
        memcpy(v_temp, v, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_temp[ju[i]] += w[kw[i]] * c[i];
            v_temp[jv[i]] = u_temp[ku[i]] * d[i] + c[i];
            w[jw[i]] = v_temp[kv[i]] * e[i] + d[i];
        }

        memcpy(u, u_temp, LEN_1D * sizeof(real_t));
        memcpy(v, v_temp, LEN_1D * sizeof(real_t));

        free(u_temp);
        free(v_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
