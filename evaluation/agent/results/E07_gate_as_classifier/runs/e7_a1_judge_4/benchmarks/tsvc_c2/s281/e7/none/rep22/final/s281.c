#include <stdlib.h>
#include "data.h"

real_t kernel_s281(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *x_vals = (real_t *)malloc(LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D; i++) {
            x_vals[i] = a[LEN_1D-i-1] + b[i] * c[i];
            b[i] = x_vals[i];
        }

        for (int i = 0; i < LEN_1D; i++) {
            a[i] = x_vals[i]-(real_t)1.0;
        }

        free(x_vals);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
