#include <stdlib.h>
#include "data.h"

real_t kernel_s243(void)
{
    real_t *aold = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for default(none) shared(a, aold) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            aold[i] = a[i];
        }
        #pragma omp parallel for default(none) shared(a, b, c, d, e, aold) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t t = b[i] + c[i] * d[i];
            real_t bi = t + d[i] * e[i];
            b[i] = bi;
            a[i] = bi + aold[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(aold);
    return (real_t)0;
}
