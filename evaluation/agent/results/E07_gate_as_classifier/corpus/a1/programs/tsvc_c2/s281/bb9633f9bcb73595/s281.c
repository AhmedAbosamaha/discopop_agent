#include "data.h"
#include <stdlib.h>

real_t kernel_s281(void)
{
    real_t x;
    real_t *a_orig = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy current state of a for reads in this activation
        for (int i = 0; i < LEN_1D; i++) {
            a_orig[i] = a[i];
        }

        for (int i = 0; i < LEN_1D; i++) {
            x = a_orig[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }

    free(a_orig);
    return (real_t)0;
}
