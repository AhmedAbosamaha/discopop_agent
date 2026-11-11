#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    real_t *u_inc = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_inc[i] = v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += u_inc[i];
            v[i] = u[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_inc);
    return (real_t)0;
}
