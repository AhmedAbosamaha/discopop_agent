#include "data.h"

real_t kernel_k23(void)
{
    real_t *u_inc = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_inc[i] = w[i] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += u_inc[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_inc);
    return (real_t)0;
}
