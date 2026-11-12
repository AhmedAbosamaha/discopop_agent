#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_temp = malloc(sizeof(real_t) * LEN_1D);
        real_t *v_temp = malloc(sizeof(real_t) * LEN_1D);
        memcpy(u_temp, u, sizeof(real_t) * LEN_1D);
        memcpy(v_temp, v, sizeof(real_t) * LEN_1D);

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v_temp[i + off] * c[i];
            v[i] = u_temp[i + far] * d[i] + c[i];
        }

        free(u_temp);
        free(v_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
