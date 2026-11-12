#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    real_t *u_snap = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *v_snap = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_snap[i] = u[i];
            v_snap[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v_snap[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_snap[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_snap);
    free(v_snap);
    return (real_t)0;
}
