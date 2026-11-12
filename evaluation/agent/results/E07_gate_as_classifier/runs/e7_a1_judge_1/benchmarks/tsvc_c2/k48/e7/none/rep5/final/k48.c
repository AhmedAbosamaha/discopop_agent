#include "data.h"

real_t kernel_k48(void)
{
    real_t *u_new = malloc(LEN_1D * sizeof(real_t));
    real_t *v_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_new[i] = u[ju[i]] + v[kv[i]] * c[i];
            v_new[i] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] = u_new[i];
            v[jv[i]] = v_new[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_new);
    free(v_new);
    return (real_t)0;
}
