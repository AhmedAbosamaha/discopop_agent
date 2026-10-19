#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    int j;
    real_t *rhs = malloc((LEN_1D-1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Pass 1: read a[i+1] into rhs
        #pragma omp parallel for private(j) shared(rhs) 
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            rhs[i] = a[j];
        }
        // Pass 2: compute a[i] from rhs and b
        #pragma omp parallel for shared(rhs) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = rhs[i] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(rhs);
    return (real_t)0;
}
