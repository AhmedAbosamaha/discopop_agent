#include "data.h"

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_saved = (real_t *)malloc(sizeof(real_t) * (2 * LEN_1D));
        for (long i = 0; i < LEN_1D; i++) {
            u_saved[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_saved[i + far] * d[i] + c[i];
        }
        free(u_saved);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
