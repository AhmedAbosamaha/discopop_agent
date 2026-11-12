#include "data.h"
#include <stdlib.h>

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *ce_sum = (real_t *)malloc(LEN_1D * sizeof(real_t));

        for (int i = 1; i < LEN_1D; i++) {
            ce_sum[i] = c[i] * (d[i] + e[i]);
        }

        for (int i = 2; i < LEN_1D; i++) {
            ce_sum[i] += ce_sum[i-1];
        }

        for (int i = 1; i < LEN_1D; i++) {
            b[i] = b[0] + ce_sum[i];
            a[i] = b[0] + (i > 1 ? ce_sum[i-1] : 0) + c[i] * d[i];
        }

        free(ce_sum);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
