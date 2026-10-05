#include <stdlib.h>
#include "data.h"

real_t kernel_s112(void)
{
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: compute from the old a[] only */
        #pragma omp parallel for default(none) shared(a, b, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            tmp[i] = a[i] + b[i];
        }
        /* pass 2: store shifted results */
        #pragma omp parallel for default(none) shared(a, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = tmp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
