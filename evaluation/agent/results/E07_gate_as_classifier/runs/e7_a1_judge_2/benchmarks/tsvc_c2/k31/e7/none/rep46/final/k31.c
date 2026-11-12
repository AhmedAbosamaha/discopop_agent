#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *v_save = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            v_save[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v_save[i + off] * c[i];
            v[i] = u[i + far] * d[i] + c[i];
        }
        free(v_save);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
