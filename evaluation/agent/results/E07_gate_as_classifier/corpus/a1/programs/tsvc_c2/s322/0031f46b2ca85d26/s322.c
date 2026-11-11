#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s322(void)
{
    real_t *a_base = (real_t*)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_base, a, LEN_1D * sizeof(real_t));
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a_base[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_base);
    return (real_t)0;
}
