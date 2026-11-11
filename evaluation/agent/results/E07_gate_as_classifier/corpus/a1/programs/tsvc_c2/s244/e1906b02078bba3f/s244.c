#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *saved_a = malloc((LEN_1D) * sizeof(real_t));
        memcpy(saved_a, a, LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            a[i+1] = b[i] + saved_a[i+1] * d[i];
        }

        free(saved_a);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
