#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    real_t *u_new = malloc(LEN_1D * sizeof(real_t));
    real_t *v_new = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_new[i] = u[i];
            v_new[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_new[i] += v_new[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v_new[i] = u_new[i + far] * d[i] + c[i];
        }
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_new[i];
            v[i] = v_new[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_new);
    free(v_new);
    return (real_t)0;
}
