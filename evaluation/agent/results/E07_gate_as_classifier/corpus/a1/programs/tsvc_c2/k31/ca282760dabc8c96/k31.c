#include "data.h"

real_t kernel_k31(void)
{
    real_t *v_old = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(v_old, v, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v_old[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(v_old);
    return (real_t)0;
}
