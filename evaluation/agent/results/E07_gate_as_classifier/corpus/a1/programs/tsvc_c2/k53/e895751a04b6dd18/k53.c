#include "data.h"

real_t kernel_k53(void)
{
    real_t *temp_v = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *temp_c = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            temp_v[i] = v[kv[i]];
            temp_c[i] = c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += temp_v[i] * temp_c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp_v);
    free(temp_c);
    return (real_t)0;
}
