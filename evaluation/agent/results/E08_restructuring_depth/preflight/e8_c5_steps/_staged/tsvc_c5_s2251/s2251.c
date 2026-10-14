#include <stdlib.h>
#include "data.h"

real_t kernel_s2251(void)
{
    real_t *tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            tmp[i] = b[i]+c[i];
        }
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = (i > 0) ? tmp[i-1] : (real_t)0.0;
            a[i] = s*e[i];
            b[i] = a[i]+d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
