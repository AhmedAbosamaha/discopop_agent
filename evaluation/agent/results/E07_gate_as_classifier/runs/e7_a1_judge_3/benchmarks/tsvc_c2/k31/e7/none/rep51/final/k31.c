#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    real_t *v_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
    memcpy(v_prev, v, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v_prev[i + off] * c[i];
            v_prev[i] = u[i + far] * d[i] + c[i];
        }
        memcpy(v, v_prev, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(v_prev);
    return (real_t)0;
}
