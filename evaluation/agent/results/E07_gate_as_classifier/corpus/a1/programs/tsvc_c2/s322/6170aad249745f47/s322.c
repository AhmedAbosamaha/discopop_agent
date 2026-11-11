#include "data.h"

real_t kernel_s322(void)
{
    real_t *a_new = (real_t*)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 2; i < LEN_1D; i++) {
            a_new[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a_new[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_new);
    return (real_t)0;
}
