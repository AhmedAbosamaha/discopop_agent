#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_copy) 
        for (int i = 0; i < LEN_1D; ++i) {
            a_copy[i] = a[i];
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        if (LEN_1D > 1) {
            a[LEN_1D-1] = b[LEN_1D-2] + a_copy[LEN_1D-1] * d[LEN_1D-2];
        }
        dummy(a, b, c, d, e);
    }

    free(a_copy);
    return (real_t)0;
}
