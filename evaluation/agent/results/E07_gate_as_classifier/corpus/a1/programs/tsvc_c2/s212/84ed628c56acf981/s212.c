#include "data.h"

real_t kernel_s212(void)
{
    real_t *a_prev = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            a_prev[i] = a[i];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
            b[i] += a_prev[i + 1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_prev);
    return (real_t)0;
}
