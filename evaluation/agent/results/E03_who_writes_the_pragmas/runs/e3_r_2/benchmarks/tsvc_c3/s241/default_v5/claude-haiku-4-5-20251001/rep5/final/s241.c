#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    real_t *a_tmp = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_tmp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a_tmp[i+1] = a[i+1];
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }
        #pragma omp parallel for shared(a_tmp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a_tmp[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_tmp);
    return (real_t)0;
}
