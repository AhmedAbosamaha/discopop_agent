#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    long u_old_size = LEN_1D + (far > 0 ? far : 0);
    real_t *u_old = malloc(u_old_size * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        long start_idx = (far < 0) ? (1 + far) : 1;
        long end_idx = LEN_1D + (far > 0 ? far : 0);
        for (long i = start_idx; i < end_idx; i++) {
            u_old[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = (far > 0 ? u_old[i + far] : u[i + far]) * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_old);
    return (real_t)0;
}
