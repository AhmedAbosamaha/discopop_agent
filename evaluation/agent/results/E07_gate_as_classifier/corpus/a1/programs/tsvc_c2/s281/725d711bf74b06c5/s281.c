#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(a_copy, a, LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D; i++) {
            x = a_copy[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        free(a_copy);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
