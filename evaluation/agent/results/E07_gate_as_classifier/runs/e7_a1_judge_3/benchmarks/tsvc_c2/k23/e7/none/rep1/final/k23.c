#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    real_t *u_accum = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *v_accum = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (long i = 0; i < LEN_1D; i++) {
        u_accum[i] = 0.0;
        v_accum[i] = 0.0;
    }

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_accum[i] += w[i] * c[i];
            v_accum[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[i] += u_accum[i];
        v[i] = v_accum[i];
    }

    free(u_accum);
    free(v_accum);
    return (real_t)0;
}
