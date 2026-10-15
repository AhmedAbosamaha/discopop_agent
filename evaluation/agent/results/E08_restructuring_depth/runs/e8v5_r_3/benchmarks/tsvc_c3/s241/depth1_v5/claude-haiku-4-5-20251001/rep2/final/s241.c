#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    real_t *a_old = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *a_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *b_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_old) 
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }
        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a_new[i] = b[i] * c[i  ] * d[i];
        }
        #pragma omp parallel for shared(b_new,a_new,a_old) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b_new[i] = a_new[i] * a_old[i+1] * d[i];
        }
        #pragma omp parallel for shared(a_new,b_new) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_new[i];
            b[i] = b_new[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_old);
    free(a_new);
    free(b_new);
    return (real_t)0;
}
