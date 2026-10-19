#include <stdlib.h>
#include "data.h"

real_t kernel_s241(void)
{
    real_t *old_a = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(old_a) 
        for (int i = 0; i < LEN_1D; i++) {
            old_a[i] = a[i];
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }
        #pragma omp parallel for shared(old_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * old_a[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(old_a);
    return (real_t)0;
}
