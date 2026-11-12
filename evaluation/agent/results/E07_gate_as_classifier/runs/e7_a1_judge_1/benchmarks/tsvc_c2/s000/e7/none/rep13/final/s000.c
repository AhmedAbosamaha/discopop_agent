#include "data.h"

real_t kernel_s000(void)
{
    real_t * b_copy = (real_t *)malloc(iterations * LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(&b_copy[nl * LEN_1D], b, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b_copy[nl * LEN_1D + i] + 1;
        }
    }

    free(b_copy);
    return (real_t)0;
}
