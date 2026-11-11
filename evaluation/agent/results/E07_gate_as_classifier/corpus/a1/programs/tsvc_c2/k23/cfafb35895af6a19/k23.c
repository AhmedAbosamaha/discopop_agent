#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_new[i] = u[i] + w[i] * c[i];
            v_new[i] = x[i] * d[i] + c[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_new[i];
            v[i] = v_new[i];
        }

        free(u_new);
        free(v_new);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
