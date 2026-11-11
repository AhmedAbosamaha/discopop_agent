#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *b_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(b_prev, b, LEN_1D * sizeof(real_t));
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b_prev[i-1] + c[i] * d[i];
            real_t b_new = a[i] + c[i] * e[i];
            b[i] = b_new;
            b_prev[i] = b_new;
        }
        free(b_prev);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
