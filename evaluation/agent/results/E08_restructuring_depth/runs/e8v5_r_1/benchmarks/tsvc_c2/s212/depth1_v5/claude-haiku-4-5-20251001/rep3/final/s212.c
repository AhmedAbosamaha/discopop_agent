#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    real_t *a_temp = (real_t *)malloc((LEN_1D) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }
        #pragma omp parallel for shared(a_temp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a_temp[i] = a[i] * c[i];
        }
        #pragma omp parallel for shared(a_temp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_temp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_temp);
    return (real_t)0;
}
