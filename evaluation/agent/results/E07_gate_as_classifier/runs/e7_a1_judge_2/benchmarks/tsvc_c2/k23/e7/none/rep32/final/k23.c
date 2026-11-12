#include "data.h"

real_t kernel_k23(void)
{
    real_t *local_w = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (long i = 0; i < LEN_1D; i++) {
        local_w[i] = w[i];
    }

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += local_w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(local_w);
    return (real_t)0;
}
