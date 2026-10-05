#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: b[i] depends only on the old a[i+1] (not yet modified). */
#pragma omp parallel for default(none) shared(a, b, d) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }
        /* Pass 2: a[i] reads the completed b[i-1] (b[0] untouched by pass 1). */
#pragma omp parallel for default(none) shared(a, b, c) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
