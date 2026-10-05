#include <stdlib.h>
#include "data.h"

real_t kernel_s112(void)
{
    /* Snapshot buffer: the original descending loop only ever reads the
       pre-loop values of a[], so copying them first removes the
       anti-dependence and makes every iteration independent. */
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for default(none) shared(a, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            tmp[i] = a[i];
        }

        #pragma omp parallel for default(none) shared(a, b, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = tmp[i] + b[i];
        }
        dummy(a, b, c, d, e);
    }

    free(tmp);
    return (real_t)0;
}
