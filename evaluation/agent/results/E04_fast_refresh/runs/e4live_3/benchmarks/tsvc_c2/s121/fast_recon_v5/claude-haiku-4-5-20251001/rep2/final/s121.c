#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    int j;
    real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_copy) 
        for (int i = 0; i < LEN_1D; i++) {
            a_copy[i] = a[i];
        }
        #pragma omp parallel for private(j) shared(a_copy) 
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a[i] = a_copy[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_copy);
    return (real_t)0;
}
