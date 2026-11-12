#include "data.h"

real_t kernel_vpvtv(void)
{
    real_t *b_prev = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    real_t *c_prev = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    memcpy(b_prev, b, sizeof(real_t) * LEN_1D);
    memcpy(c_prev, c, sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            a[i] += b_prev[i] * c_prev[i];
        }
        dummy(a, b, c, d, e);
        memcpy(b_prev, b, sizeof(real_t) * LEN_1D);
        memcpy(c_prev, c, sizeof(real_t) * LEN_1D);
    }

    free(b_prev);
    free(c_prev);
    return (real_t)0;
}
