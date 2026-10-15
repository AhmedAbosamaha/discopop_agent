#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s127(void)
{
    real_t *b_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(b_copy, b, LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(b_copy) 
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b_copy[i] + c[i] * d[i];
            a[2*i + 1] = b_copy[i] + d[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }

    free(b_copy);
    return (real_t)0;
}
