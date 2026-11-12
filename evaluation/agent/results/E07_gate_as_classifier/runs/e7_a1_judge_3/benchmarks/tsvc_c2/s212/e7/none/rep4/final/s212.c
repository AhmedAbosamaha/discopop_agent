#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* a_prev = (real_t*)malloc(LEN_1D * sizeof(real_t));
        memcpy(a_prev, a, LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
            b[i] += a_prev[i + 1] * d[i];
        }

        free(a_prev);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
