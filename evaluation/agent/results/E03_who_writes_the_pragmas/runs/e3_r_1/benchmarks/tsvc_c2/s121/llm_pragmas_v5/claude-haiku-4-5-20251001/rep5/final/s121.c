#include "data.h"
#include <string.h>
#include <stdlib.h>

real_t kernel_s121(void)
{
    int j;
    real_t *a_copy = (real_t*)malloc(LEN_1D * sizeof(real_t));

    #pragma omp parallel
    {
        for (int nl = 0; nl < iterations; nl++) {
            #pragma omp for
            for (int k = 0; k < LEN_1D; k++) {
                a_copy[k] = a[k];
            }

            #pragma omp for private(j)
            for (int i = 0; i < LEN_1D-1; i++) {
                j = i + 1;
                a[i] = a_copy[j] + b[i];
            }

            #pragma omp single
            dummy(a, b, c, d, e);
        }
    }
    free(a_copy);
    return (real_t)0;
}
