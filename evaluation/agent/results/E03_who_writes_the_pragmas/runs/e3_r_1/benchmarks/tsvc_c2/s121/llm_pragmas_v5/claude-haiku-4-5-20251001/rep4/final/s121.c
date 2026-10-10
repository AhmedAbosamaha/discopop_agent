#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s121(void)
{
    real_t *a_copy = malloc(LEN_1D * sizeof(real_t));

    #pragma omp parallel shared(a, a_copy, b)
    {
        for (int nl = 0; nl < iterations; nl++) {
            #pragma omp for schedule(static)
            for (int i = 0; i < LEN_1D; i++) {
                a_copy[i] = a[i];
            }

            #pragma omp for schedule(static)
            for (int i = 0; i < LEN_1D-1; i++) {
                a[i] = a_copy[i + 1] + b[i];
            }

            #pragma omp single
            {
                dummy(a, b, c, d, e);
            }
        }
    }

    free(a_copy);
    return (real_t)0;
}
