#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    real_t *u_old = malloc(LEN_1D * sizeof(real_t));
    real_t *v_old = malloc(LEN_1D * sizeof(real_t));
    real_t *u_new = malloc(LEN_1D * sizeof(real_t));
    real_t *v_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(u_old, u, LEN_1D * sizeof(real_t));
        memcpy(v_old, v, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_new[i] = u_old[i] + v_old[i + off] * c[i];
            v_new[i] = u_old[i + far] * d[i] + c[i];
        }
        memcpy(u + 1, u_new + 1, (LEN_1D - 1) * sizeof(real_t));
        memcpy(v + 1, v_new + 1, (LEN_1D - 1) * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(u_old);
    free(v_old);
    free(u_new);
    free(v_new);
    return (real_t)0;
}
