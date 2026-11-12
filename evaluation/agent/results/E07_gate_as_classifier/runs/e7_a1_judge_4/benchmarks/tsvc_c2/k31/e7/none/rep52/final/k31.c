#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_old = malloc(LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            u_old[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            real_t u_val = (i + far < i) ? u[i + far] : u_old[i + far];
            v[i] = u_val * d[i] + c[i];
        }
        free(u_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
