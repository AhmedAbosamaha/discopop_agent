#include "data.h"

real_t kernel_k23(void)
{
    real_t *delta = malloc(sizeof(real_t) * LEN_1D);
    memset(delta, 0, sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            delta[i] += w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[i] += delta[i];
    }

    free(delta);
    return (real_t)0;
}
