#include "data.h"

real_t kernel_s000(void)
{
    real_t *b_copy = malloc(LEN_1D * sizeof(real_t));
    memcpy(b_copy, b, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b_copy[i] + 1;
        }
        dummy(a, b, c, d, e);
    }

    free(b_copy);
    return (real_t)0;
}
