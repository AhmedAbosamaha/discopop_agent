#include "data.h"
#include <stdlib.h>

real_t kernel_s211(void)
{
    real_t *new_b = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        new_b[0] = b[0];
        for (int i = 1; i < LEN_1D-1; i++) {
            new_b[i] = b[i + 1] - e[i] * d[i];
        }
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = new_b[i - 1] + c[i] * d[i];
        }
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = new_b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(new_b);
    return (real_t)0;
}
