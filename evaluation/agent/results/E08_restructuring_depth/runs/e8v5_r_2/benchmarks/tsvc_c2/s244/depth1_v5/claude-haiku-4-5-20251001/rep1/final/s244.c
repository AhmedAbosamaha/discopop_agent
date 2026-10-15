#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    real_t* a_orig = (real_t*)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_orig) 
        for (int i = 0; i < LEN_1D; ++i) {
            a_orig[i] = a[i];
            if (i < LEN_1D-1) {
                a[i] = b[i] + c[i] * d[i];
            }
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + a_orig[LEN_1D-1] * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    free(a_orig);
    return (real_t)0;
}
