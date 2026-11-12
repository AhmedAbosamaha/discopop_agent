#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s000(void)
{
    real_t * b_copy = (real_t *)malloc(iterations * LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations - 1; nl++) {
        memcpy(&b_copy[nl * LEN_1D], b, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    memcpy(&b_copy[(iterations - 1) * LEN_1D], b, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for firstprivate(nl) shared(b_copy) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b_copy[nl * LEN_1D + i] + 1;
        }
    }

    dummy(a, b, c, d, e);

    free(b_copy);
    return (real_t)0;
}
