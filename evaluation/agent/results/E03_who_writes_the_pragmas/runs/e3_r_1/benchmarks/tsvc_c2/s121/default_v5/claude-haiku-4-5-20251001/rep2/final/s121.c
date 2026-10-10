#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    int j;
    real_t *a_old = malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_old) 
        for (int k = 0; k < LEN_1D; k++) {
            a_old[k] = a[k];
        }
        #pragma omp parallel for private(j) shared(a_old) 
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a[i] = a_old[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_old);
    return (real_t)0;
}
