#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    real_t *a_orig = (real_t *)malloc(LEN_1D * sizeof(real_t));
    #pragma omp parallel for shared(a_orig) 
    for (int k = 0; k < LEN_1D; k++) {
        a_orig[k] = a[k];
    }
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_orig) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
            b[i] += a_orig[i + 1] * d[i];
        }
        dummy(a, b, c, d, e);
        #pragma omp parallel for shared(a_orig) 
        for (int k = 0; k < LEN_1D; k++) {
            a_orig[k] = a[k];
        }
    }
    free(a_orig);
    return (real_t)0;
}
