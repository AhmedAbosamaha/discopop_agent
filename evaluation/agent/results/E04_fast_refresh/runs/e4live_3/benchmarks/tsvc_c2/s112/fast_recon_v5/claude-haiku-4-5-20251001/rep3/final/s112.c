#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    real_t *temp = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        // Read phase: snapshot array a into temp
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D - 1; i++) {
            temp[i] = a[i];
        }
        // Write phase: compute results from snapshot
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = temp[i] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
