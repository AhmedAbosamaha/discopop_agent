#include "data.h"

real_t kernel_k53(void)
{
    real_t *v_snapshot = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        memcpy(v_snapshot, v, LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_snapshot[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(v_snapshot);
    return (real_t)0;
}
