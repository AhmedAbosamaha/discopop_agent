#include "data.h"

real_t kernel_s321(void)
{
    real_t *prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
    memcpy(prev, a, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = prev[i] + prev[i-1] * b[i];
        }
        memcpy(prev, a, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(prev);
    return (real_t)0;
}
