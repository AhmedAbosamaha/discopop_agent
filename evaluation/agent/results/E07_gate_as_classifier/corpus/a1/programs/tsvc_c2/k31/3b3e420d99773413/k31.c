#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_save = NULL;
        long u_save_min = 0;

        // Only save original u values when far > 0; when far <= 0, iteration i reads
        // the current value of u[i+far] after it has been modified by iteration i+far
        if (far > 0) {
            u_save_min = 1;
            long u_save_max = (LEN_1D - 1) + far;
            u_save = (real_t *)malloc((u_save_max - u_save_min + 1) * sizeof(real_t));
            for (long i = u_save_min; i <= u_save_max; i++) {
                u_save[i - u_save_min] = u[i];
            }
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            if (far > 0) {
                v[i] = u_save[i + far - u_save_min] * d[i] + c[i];
            } else {
                v[i] = u[i + far] * d[i] + c[i];
            }
        }

        if (u_save != NULL) {
            free(u_save);
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
