#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    real_t *saved_a = (real_t *) malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(saved_a) 
        for (int i = 0; i < LEN_1D; ++i) {
            saved_a[i] = a[i];
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + saved_a[LEN_1D-1] * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    free(saved_a);
    return (real_t)0;
}
