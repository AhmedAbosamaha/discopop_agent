#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    real_t *u_old = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(u_old) 
        for (long i = 0; i < LEN_1D; i++) {
            u_old[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u_old[i] + v[i + off] * c[i];
            v[i] = u[i + far] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_old);
    return (real_t)0;
}
