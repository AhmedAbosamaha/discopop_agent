#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save old values to break loop-carried dependence on a[i+1]
        real_t* old_a = (real_t*)malloc(LEN_1D * sizeof(real_t));
        real_t* old_b = (real_t*)malloc(LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(old_b,old_a) 
        for (int i = 0; i < LEN_1D; i++) {
            old_a[i] = a[i];
            old_b[i] = b[i];
        }

        #pragma omp parallel for shared(old_b,old_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = old_b[i] * c[i  ] * d[i];
            b[i] = a[i] * old_a[i+1] * d[i];
        }

        free(old_a);
        free(old_b);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
