#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s322(void)
{
    real_t *a_prev = (real_t*)malloc(LEN_1D * sizeof(real_t));
    memcpy(a_prev, a, LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a[i] + a_prev[i - 1] * b[i] + a_prev[i - 2] * c[i];
        }
        memcpy(a_prev, a, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }
    free(a_prev);
    return (real_t)0;
}
