#include "data.h"

real_t kernel_k53(void)
{
    real_t *v_saved = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            v_saved[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_saved[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(v_saved);
    return (real_t)0;
}
