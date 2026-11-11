#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    real_t *a_save = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int j = 0; j < LEN_1D; ++j) {
            a_save[j] = a[j];
        }
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            a[i+1] = b[i] + a_save[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_save);
    return (real_t)0;
}
