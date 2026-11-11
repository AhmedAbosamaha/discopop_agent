#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *saved_b = malloc((LEN_1D) * sizeof(real_t));
        memcpy(saved_b, b, LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i+1] = saved_b[i] + a[i+1] * d[i];
            b[i] = c[i] + saved_b[i];
        }
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = saved_b[i] + c[i] * d[i];
        }

        free(saved_b);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
