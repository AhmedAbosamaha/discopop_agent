#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    real_t *temp = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D - 1; i++) {
            temp[i] = a[i + 1];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
            b[i] += temp[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
