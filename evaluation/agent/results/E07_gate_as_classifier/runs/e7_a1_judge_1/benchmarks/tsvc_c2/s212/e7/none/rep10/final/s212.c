#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_old = malloc(sizeof(real_t) * LEN_1D);
        memcpy(a_old, a, sizeof(real_t) * LEN_1D);

        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }

        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a_old[i + 1] * d[i];
        }

        free(a_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
