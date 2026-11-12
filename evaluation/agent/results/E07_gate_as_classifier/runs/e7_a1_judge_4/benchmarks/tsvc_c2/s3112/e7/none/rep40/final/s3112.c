#include "data.h"
#include <stdlib.h>

real_t kernel_s3112(void)
{
    real_t sum;
    real_t *cumsum = malloc((LEN_1D + 1) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        cumsum[0] = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            cumsum[i+1] = cumsum[i] + a[i];
            b[i] = cumsum[i+1];
        }
        sum = cumsum[LEN_1D];
        dummy(a, b, c, d, e);
    }
    free(cumsum);
    return sum;
}
