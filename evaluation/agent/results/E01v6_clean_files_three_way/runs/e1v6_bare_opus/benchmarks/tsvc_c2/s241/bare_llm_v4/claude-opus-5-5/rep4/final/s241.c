#include <stdlib.h>
#include "data.h"

real_t kernel_s241(void)
{
    real_t *t = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        /* phase 1: new a values into t; b uses old a[i+1] (a not written here) */
#pragma omp parallel for default(none) shared(a, b, c, d, t) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            t[i] = b[i] * c[i  ] * d[i];
            b[i] = t[i] * a[i+1] * d[i];
        }
        /* phase 2: commit new a values */
#pragma omp parallel for default(none) shared(a, t) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = t[i];
        }
        dummy(a, b, c, d, e);
    }
    free(t);
    return (real_t)0;
}
