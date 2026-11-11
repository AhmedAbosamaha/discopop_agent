#include <stdlib.h>
#include "data.h"

real_t kernel_s321(void)
{
    real_t *tmp = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        tmp[0] = a[0];
        for (int i = 1; i < LEN_1D; i++) {
            tmp[i] = a[i] + tmp[i-1] * b[i];
            a[i] = tmp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
