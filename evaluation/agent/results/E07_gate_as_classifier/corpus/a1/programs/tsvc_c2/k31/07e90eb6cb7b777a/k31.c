#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    real_t *u_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(u_new, u, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_new[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_new[i + far] * d[i] + c[i];
        }

        memcpy(u, u_new, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(u_new);
    return (real_t)0;
}
