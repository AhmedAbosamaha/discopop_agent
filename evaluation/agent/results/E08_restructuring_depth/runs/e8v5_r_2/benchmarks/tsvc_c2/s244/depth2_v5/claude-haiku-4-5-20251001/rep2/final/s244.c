#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    real_t *c_copy = malloc(LEN_1D * sizeof(real_t));
    real_t *d_copy = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        if (nl > 0) {
            dummy(a, b, c, d, e);
        }
        #pragma omp parallel for shared(d_copy,c_copy) 
        for (int i = 0; i < LEN_1D; i++) {
            c_copy[i] = c[i];
            d_copy[i] = d[i];
        }
        #pragma omp parallel for shared(d_copy,c_copy) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c_copy[i] * d_copy[i];
            b[i] = c_copy[i] + b[i];
        }
        if (LEN_1D > 1) {
            a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d_copy[LEN_1D-2];
        }
    }
    if (iterations > 0) {
        dummy(a, b, c, d, e);
    }

    free(c_copy);
    free(d_copy);
    return (real_t)0;
}
