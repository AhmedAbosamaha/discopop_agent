#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s321(void)
{
    real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));
    memcpy(a_copy, a, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            a_copy[i] += a_copy[i-1] * b[i];
        }
        memcpy(a, a_copy, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(a_copy);
    return (real_t)0;
}
