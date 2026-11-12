#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save original u values before modifications
        long u_save_min = 1 + (far < 0 ? far : 0);
        long u_save_max = (LEN_1D - 1) + (far > 0 ? far : 0);
        real_t *u_save = (real_t *)malloc((u_save_max - u_save_min + 1) * sizeof(real_t));
        for (long i = u_save_min; i <= u_save_max; i++) {
            u_save[i - u_save_min] = u[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_save[i + far - u_save_min] * d[i] + c[i];
        }
        free(u_save);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
