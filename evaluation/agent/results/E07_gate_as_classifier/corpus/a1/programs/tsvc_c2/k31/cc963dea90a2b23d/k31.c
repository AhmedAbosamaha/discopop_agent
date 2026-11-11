#include <stdlib.h>
#include "data.h"

real_t kernel_k31(void)
{
    real_t *u_prev = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_prev[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = ((far > 0) ? u_prev[i + far] : u[i + far]) * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_prev);
    return (real_t)0;
}
