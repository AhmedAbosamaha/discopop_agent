#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    real_t *a_orig = malloc(LEN_1D * sizeof(real_t));
    #pragma omp parallel
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp for
        for (int j = 0; j < LEN_1D; j++) {
            a_orig[j] = a[j];
        }
        #pragma omp for schedule(auto)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = a_orig[i] + b[i];
        }
        #pragma omp single
        dummy(a, b, c, d, e);
        #pragma omp barrier
    }
    free(a_orig);
    return (real_t)0;
}
