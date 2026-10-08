#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* a_saved = (real_t*)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(a_saved) 
        for (int i = 0; i < LEN_1D; i++) {
            a_saved[i] = a[i];
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }
        #pragma omp parallel for shared(a_saved) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a_saved[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
        free(a_saved);
    }
    return (real_t)0;
}
