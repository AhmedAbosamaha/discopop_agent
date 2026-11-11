#include "data.h"

real_t kernel_k31(void)
{
    real_t *u_temp = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_temp[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_temp[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_temp);
    return (real_t)0;
}
