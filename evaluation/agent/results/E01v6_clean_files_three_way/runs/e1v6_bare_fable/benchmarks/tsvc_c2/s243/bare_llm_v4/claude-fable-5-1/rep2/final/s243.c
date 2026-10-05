#include <stdlib.h>
#include "data.h"

real_t kernel_s243(void)
{
    /* Snapshot of a[] taken before each sweep so that the read of the
       old a[i+1] no longer depends on iteration i+1 not having run yet. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    if (a_old == NULL) return (real_t)0;

    for (int nl = 0; nl < iterations; nl++) {
        /* Copy the whole array: iteration LEN_1D-2 reads a[LEN_1D-1]. */
#pragma omp parallel for default(none) shared(a, a_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

#pragma omp parallel for default(none) shared(a, b, c, d, e, a_old) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
