#include "data.h"
#include <stdlib.h>

real_t kernel_s321(void)
{
    real_t *tmp = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            tmp[i] = a[i-1] * b[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += tmp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
