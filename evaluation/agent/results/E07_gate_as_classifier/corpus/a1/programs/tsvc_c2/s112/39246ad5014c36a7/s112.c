#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(a_temp) 
        for (int i = 0; i < LEN_1D; i++) {
            a_temp[i] = a[i];
        }
        #pragma omp parallel for shared(a_temp) 
        for (int i = LEN_1D - 2; i >= 0; i--) {
            a[i+1] = a_temp[i] + b[i];
        }
        free(a_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
