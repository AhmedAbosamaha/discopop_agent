#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    real_t *accu_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
    #pragma omp parallel for shared(accu_u) 
    for (long i = 0; i < LEN_1D; i++) {
        accu_u[i] = 0.0;
    }
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            accu_u[i] += w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    for (long i = 1; i < LEN_1D; i++) {
        u[i] += accu_u[i];
    }
    free(accu_u);
    return (real_t)0;
}
