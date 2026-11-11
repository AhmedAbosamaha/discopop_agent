#include "data.h"
#include <string.h>

real_t kernel_s161(void)
{
    real_t *c_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(c_temp, c, LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            } else {
                a[i] = c_temp[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(c_temp);
    return (real_t)0;
}
