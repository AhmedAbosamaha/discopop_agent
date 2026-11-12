#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *b_old = malloc(LEN_1D * sizeof(real_t));
        memcpy(b_old, b, LEN_1D * sizeof(real_t));
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b_old[i-1] + c[i] * d[i];
            b[i] = a[i] + c[i] * e[i];
        }
        free(b_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
