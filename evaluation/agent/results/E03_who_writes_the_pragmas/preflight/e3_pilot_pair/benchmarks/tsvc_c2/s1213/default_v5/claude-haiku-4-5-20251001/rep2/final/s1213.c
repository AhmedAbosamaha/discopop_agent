#include "data.h"
#include <stdlib.h>

real_t kernel_s1213(void)
{
    real_t *b_new = (real_t*)malloc(LEN_1D * sizeof(real_t));
    b_new[0] = b[0];
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            b_new[i] = a[i+1]*d[i];
        }
        #pragma omp parallel for shared(b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b_new[i-1]+c[i];
        }
        #pragma omp parallel for shared(b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_new[i];
        }
        dummy(a, b, c, d, e);
    }
    free(b_new);
    return (real_t)0;
}
