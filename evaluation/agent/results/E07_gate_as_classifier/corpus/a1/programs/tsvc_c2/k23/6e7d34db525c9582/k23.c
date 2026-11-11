#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    real_t *temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            temp[i] = w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        #pragma omp parallel for shared(temp) 
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += temp[i];
        }
        dummy(a, b, c, d, e);
    }

    free(temp);
    return (real_t)0;
}
