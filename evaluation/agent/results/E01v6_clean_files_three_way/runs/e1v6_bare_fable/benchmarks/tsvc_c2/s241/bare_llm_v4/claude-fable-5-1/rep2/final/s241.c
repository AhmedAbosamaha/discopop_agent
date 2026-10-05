#include <stdlib.h>
#include "data.h"

real_t kernel_s241(void)
{
    /* Heap temp for the new values of a[]: lets every iteration read the
       OLD a[i+1] without waiting for iteration i+1 to finish. */
    real_t *anew = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    if (anew == NULL) return (real_t)0;

    for (int nl = 0; nl < iterations; nl++) {
        /* Loop 1: reads old a, old b; writes anew[i] and b[i] only. */
#pragma omp parallel for default(none) shared(a, b, c, d, anew) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            anew[i] = b[i] * c[i  ] * d[i];
            b[i] = anew[i] * a[i+1] * d[i];
        }
        /* Loop 2: commit the new a values (same range as the original). */
#pragma omp parallel for default(none) shared(a, anew) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = anew[i];
        }
        dummy(a, b, c, d, e);
    }

    free(anew);
    return (real_t)0;
}
