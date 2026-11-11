#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_vpvtv(void)
{
    real_t *b_prev = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    memcpy(b_prev, b, sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(b_prev) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] += b_prev[i] * c[i];
        }
        dummy(a, b, c, d, e);
        memcpy(b_prev, b, sizeof(real_t) * LEN_1D);
    }

    free(b_prev);
    return (real_t)0;
}
