#include "data.h"
#include <stdlib.h>

real_t kernel_s322(void)
{
    real_t *temp_b = (real_t*)malloc(LEN_1D * sizeof(real_t));
    real_t *temp_c = (real_t*)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 2; i < LEN_1D; i++) {
            temp_b[i] = a[i - 1] * b[i];
            temp_c[i] = a[i - 2] * c[i];
        }
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a[i] + temp_b[i] + temp_c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp_b);
    free(temp_c);
    return (real_t)0;
}
