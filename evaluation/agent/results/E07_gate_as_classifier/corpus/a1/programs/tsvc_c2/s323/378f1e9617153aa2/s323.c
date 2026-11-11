#include <stdlib.h>
#include "data.h"

real_t kernel_s323(void)
{
    real_t *prefix = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        prefix[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            prefix[i] = prefix[i-1] + c[i] * (d[i] + e[i]);
        }
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[0] + prefix[i-1] + c[i] * d[i];
            b[i] = b[0] + prefix[i];
        }
        dummy(a, b, c, d, e);
    }
    free(prefix);
    return (real_t)0;
}
