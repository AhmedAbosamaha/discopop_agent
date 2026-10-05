#include <stdlib.h>
#include "data.h"

real_t kernel_s243(void)
{
    real_t *aold = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        /* snapshot old a values: iteration i reads a[i+1] before it is overwritten */
#pragma omp parallel for default(none) shared(a, aold) schedule(static)
        for (int i = 1; i < LEN_1D; i++) {
            aold[i] = a[i];
        }
#pragma omp parallel for default(none) shared(a, b, c, d, e, aold) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t ai = b[i] + c[i] * d[i];
            real_t bi = ai + d[i] * e[i];
            b[i] = bi;
            a[i] = bi + aold[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(aold);
    return (real_t)0;
}
