#include "data.h"
#include <stdlib.h>

real_t kernel_s321(void)
{
    real_t *prod = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            prod[i] = a[i-1] * b[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += prod[i];
        }
        dummy(a, b, c, d, e);
    }

    free(prod);
    return (real_t)0;
}
