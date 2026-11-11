#include "data.h"
#include <string.h>
#include <stdlib.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_old = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_old = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(u_old, u, LEN_1D * sizeof(real_t));
        memcpy(v_old, v, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v_old[i + off] * c[i];
            v[i] = u_old[i + far] * d[i] + c[i];
        }

        free(u_old);
        free(v_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
