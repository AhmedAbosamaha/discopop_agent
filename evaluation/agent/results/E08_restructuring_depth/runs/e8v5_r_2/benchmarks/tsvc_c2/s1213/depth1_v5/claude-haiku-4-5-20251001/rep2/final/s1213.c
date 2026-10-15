#include "data.h"
#include <stdlib.h>

real_t kernel_s1213(void)
{
    real_t *a_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }
        #pragma omp parallel for shared(a_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            a_new[i] = b[i-1]+c[i];
        }
        #pragma omp parallel for shared(a_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = a_new[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_new);
    return (real_t)0;
}
