#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    /* Scratch buffer holding the new values of b for one sweep.  Heap
       allocated once: its size grows with LEN_1D. */
    real_t *bn = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* b[0] is never written by the sweep, so the "new" b[0] is b[0]. */
        bn[0] = b[0];

        /* Phase 1: new b values depend only on OLD b (b[i+1] is not yet
           written in the original order), so iterations are independent. */
#pragma omp parallel for default(none) shared(b, d, e, bn) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            bn[i] = b[i + 1] - e[i] * d[i];
        }

        /* Phase 2: a[i] reads the NEW b[i-1], which phase 1 has fully
           produced in bn; b[i] receives its new value. */
#pragma omp parallel for default(none) shared(a, b, c, d, bn) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = bn[i - 1] + c[i] * d[i];
            b[i] = bn[i];
        }

        dummy(a, b, c, d, e);
    }

    free(bn);
    return (real_t)0;
}
