#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *v_src = malloc(LEN_1D * sizeof(real_t));
        memcpy(v_src, v, LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_src[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        free(v_src);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
