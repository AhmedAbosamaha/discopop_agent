#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    /* Heap buffer holding the new values of b for one sweep.  Only
       indices 1..LEN_1D-2 are used. */
    real_t *bn = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: new b, computed from OLD b (anti-dependence removed by
           writing into a separate buffer). */
#pragma omp parallel for default(none) shared(b, bn, d, e) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            bn[i] = b[i + 1] - e[i] * d[i];
        }

        /* Boundary i = 1: reads b[0], which the loop never writes. */
        a[1] = b[0] + c[1] * d[1];
        b[1] = bn[1];

        /* Pass 2: a[i] uses the NEW b[i-1] (now in bn), and b takes its
           new value. */
#pragma omp parallel for default(none) shared(a, b, bn, c, d) schedule(static)
        for (int i = 2; i < LEN_1D-1; i++) {
            a[i] = bn[i - 1] + c[i] * d[i];
            b[i] = bn[i];
        }

        dummy(a, b, c, d, e);
    }

    free(bn);
    return (real_t)0;
}
