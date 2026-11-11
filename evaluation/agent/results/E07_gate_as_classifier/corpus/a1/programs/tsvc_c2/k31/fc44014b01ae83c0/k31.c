#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    real_t *u_saved = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_saved[i] = u[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_saved[i + far] * d[i] + c[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }

        dummy(a, b, c, d, e);
    }

    free(u_saved);
    return (real_t)0;
}
