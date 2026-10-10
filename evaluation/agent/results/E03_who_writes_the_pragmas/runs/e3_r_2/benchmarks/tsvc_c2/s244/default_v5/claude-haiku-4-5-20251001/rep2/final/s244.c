#include <stdlib.h>
#include "data.h"

real_t kernel_s244(void)
{
    real_t *a_temp = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_temp) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a_temp[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            a[i+1] = b[i] + a[i+1] * d[i];
        }
        #pragma omp parallel for shared(a_temp) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = a_temp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_temp);
    return (real_t)0;
}
