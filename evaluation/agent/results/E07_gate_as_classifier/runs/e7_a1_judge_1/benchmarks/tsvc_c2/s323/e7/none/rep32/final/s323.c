#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *b_temp = malloc(LEN_1D * sizeof(real_t));
        memcpy(b_temp, b, LEN_1D * sizeof(real_t));
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b_temp[i-1] + c[i] * d[i];
            b_temp[i] = a[i] + c[i] * e[i];
        }
        memcpy(b, b_temp, LEN_1D * sizeof(real_t));
        free(b_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
