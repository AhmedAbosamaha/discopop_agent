#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    real_t *cumsum = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        real_t base = a[0];

        cumsum[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            cumsum[i] = cumsum[i-1] + b[i-1];
        }

        for (int i = 1; i < LEN_1D; i++) {
            a[i] = base + cumsum[i];
        }

        dummy(a, b, c, d, e);
    }

    free(cumsum);
    return (real_t)0;
}
