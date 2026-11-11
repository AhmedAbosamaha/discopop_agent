#include "data.h"

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save current u values before they are modified
        long u_save_size = LEN_1D + 10000;
        real_t *u_old = malloc(u_save_size * sizeof(real_t));
        memcpy(u_old, u, u_save_size * sizeof(real_t));

        // Pass 1: Update u using v values
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }

        // Pass 2: Update v using saved u values from before pass 1
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_old[i + far] * d[i] + c[i];
        }

        free(u_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
