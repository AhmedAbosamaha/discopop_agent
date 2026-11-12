#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *v_temp = malloc(LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            if (i > 1) {
                v[jv[i-1]] = v_temp[jv[i-1]];
            }
            real_t v_val = v[kv[i]];
            real_t u_val = u[ku[i]];
            u[ju[i]] += v_val * c[i];
            v_temp[jv[i]] = u_val * d[i] + c[i];
        }
        v[jv[LEN_1D-1]] = v_temp[jv[LEN_1D-1]];
        free(v_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
