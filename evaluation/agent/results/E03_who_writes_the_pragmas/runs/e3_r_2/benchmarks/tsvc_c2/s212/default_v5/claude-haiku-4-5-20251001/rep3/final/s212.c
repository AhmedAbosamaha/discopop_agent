#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    real_t *temp_a = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(temp_a) 
        for (int i = 0; i < LEN_1D; i++) {
            temp_a[i] = a[i];
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        #pragma omp parallel for shared(temp_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += temp_a[i + 1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp_a);
    return (real_t)0;
}
