#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    /* Scratch copy of a[] so the shift a[i+1] = a[i] + b[i] can run with
       independent iterations: the original backward loop always reads the
       pre-loop value of a[i], which is what tmp[] holds. */
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
