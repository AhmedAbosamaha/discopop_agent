#include "data.h"

real_t kernel_k23(void)
{
    real_t *w_snap = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            w_snap[i] = w[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w_snap[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(w_snap);
    return (real_t)0;
}
