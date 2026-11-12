#include "data.h"

real_t kernel_k31(void)
{
    real_t *u_old = malloc(sizeof(real_t) * LEN_1D);
    real_t *v_old = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_old[i] = u[i];
            v_old[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_old[i] + v_old[i + off] * c[i];
        }
        real_t *u_src = (far < 0) ? u : u_old;
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_src[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_old);
    free(v_old);
    return (real_t)0;
}
