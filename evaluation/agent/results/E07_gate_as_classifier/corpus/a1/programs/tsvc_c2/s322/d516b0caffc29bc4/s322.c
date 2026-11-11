#include "data.h"

real_t kernel_s322(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* a_old = (real_t*)malloc(sizeof(real_t) * LEN_1D);
        memcpy(a_old, a, sizeof(real_t) * LEN_1D);

        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a_old[i] + a_old[i - 1] * b[i] + a_old[i - 2] * c[i];
        }

        free(a_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
