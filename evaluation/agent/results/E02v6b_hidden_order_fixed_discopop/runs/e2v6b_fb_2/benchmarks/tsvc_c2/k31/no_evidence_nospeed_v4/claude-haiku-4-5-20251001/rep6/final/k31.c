#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    real_t *v_new = malloc(sizeof(real_t) * LEN_1D);
    memcpy(v_new, v, sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(v_new) 
        for (long i = 1; i < LEN_1D; i++) {
            v_new[i] = u[i + far] * d[i] + c[i];
        }
        #pragma omp parallel for shared(v_new) 
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v_new[i + off] * c[i];
        }
        memcpy(v, v_new, sizeof(real_t) * LEN_1D);
        dummy(a, b, c, d, e);
    }

    free(v_new);
    return (real_t)0;
}
