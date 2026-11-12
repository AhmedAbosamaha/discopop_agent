#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    long u_orig_size = LEN_1D + (far > 0 ? far : 0);
    real_t *u_orig = malloc(u_orig_size * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < u_orig_size; i++) {
            u_orig[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_orig[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_orig);
    return (real_t)0;
}
