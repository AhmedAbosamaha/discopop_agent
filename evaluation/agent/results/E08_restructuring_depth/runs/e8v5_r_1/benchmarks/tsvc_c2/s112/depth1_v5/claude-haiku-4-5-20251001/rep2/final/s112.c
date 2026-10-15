#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    real_t *a_new = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        // Compute new values using original a
        a_new[0] = a[0];
        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D - 1; i++) {
            a_new[i+1] = a[i] + b[i];
        }
        // Apply updates back to a
        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a_new[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_new);
    return (real_t)0;
}
