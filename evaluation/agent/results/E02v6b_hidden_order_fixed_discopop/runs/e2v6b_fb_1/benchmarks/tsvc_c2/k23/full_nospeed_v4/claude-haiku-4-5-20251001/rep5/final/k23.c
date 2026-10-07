#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    real_t *u_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
    #pragma omp parallel for shared(u_temp) 
    for (long i = 0; i < LEN_1D; i++) {
        u_temp[i] = u[i];
    }

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_temp[i] += w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    for (long i = 0; i < LEN_1D; i++) {
        u[i] = u_temp[i];
    }
    free(u_temp);
    return (real_t)0;
}
