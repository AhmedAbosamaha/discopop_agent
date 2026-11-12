#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    real_t *u_tmp = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *v_tmp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_tmp[i] = u[i];
            v_tmp[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_tmp[i] += v_tmp[i + off] * c[i];
            v_tmp[i] = u_tmp[i + far] * d[i] + c[i];
        }
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_tmp[i];
            v[i] = v_tmp[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_tmp);
    free(v_tmp);
    return (real_t)0;
}
