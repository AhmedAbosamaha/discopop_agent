#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    static real_t *u_old = NULL, *v_old = NULL;
    if (u_old == NULL) {
        u_old = (real_t *)malloc(LEN_1D * sizeof(real_t));
        v_old = (real_t *)malloc(LEN_1D * sizeof(real_t));
    }

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_old[i] = u[i];
            v_old[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_old[i] + v_old[i + off] * c[i];
            v[i] = u_old[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
