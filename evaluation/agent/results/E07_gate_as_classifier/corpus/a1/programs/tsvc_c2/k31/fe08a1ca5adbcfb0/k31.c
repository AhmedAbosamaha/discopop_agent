#include <stdlib.h>
#include <string.h>
#include "data.h"

real_t kernel_k31(void)
{
    real_t *temp_u = malloc(LEN_1D * sizeof(real_t));
    memcpy(temp_u, u, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
            v[i] = temp_u[i + far] * d[i] + c[i];
        }
        memcpy(temp_u, u, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }
    free(temp_u);
    return (real_t)0;
}
