#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *v_temp = malloc(LEN_1D * sizeof(real_t));
        for (long i = 0; i < LEN_1D; i++) {
            v_temp[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_temp[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        free(v_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
