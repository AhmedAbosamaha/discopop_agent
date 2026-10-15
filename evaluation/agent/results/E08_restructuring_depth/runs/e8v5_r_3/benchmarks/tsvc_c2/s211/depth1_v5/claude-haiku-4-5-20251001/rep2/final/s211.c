#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s211(void)
{
    real_t *b_new = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(b_new) 
        for (int j = 0; j < LEN_1D; j++) {
            b_new[j] = b[j];
        }
        #pragma omp parallel for firstprivate(b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            b_new[i] = b[i + 1] - e[i] * d[i];
        }
        #pragma omp parallel for shared(b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b_new[i - 1] + c[i] * d[i];
        }
        #pragma omp parallel for shared(b_new) 
        for (int j = 0; j < LEN_1D; j++) {
            b[j] = b_new[j];
        }
        dummy(a, b, c, d, e);
    }
    free(b_new);
    return (real_t)0;
}
