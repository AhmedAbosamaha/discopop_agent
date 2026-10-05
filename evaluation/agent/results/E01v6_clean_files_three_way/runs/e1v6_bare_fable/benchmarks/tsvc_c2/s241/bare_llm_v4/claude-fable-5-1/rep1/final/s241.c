#include <stdlib.h>
#include "data.h"

real_t kernel_s241(void)
{
    /* Snapshot of the previous a[i+1] values: the original loop reads
       a[i+1] before iteration i+1 overwrites it (anti-dependence). */
    real_t *old_a = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    if (old_a == NULL) return (real_t)0;

    for (int nl = 0; nl < iterations; nl++) {
        /* Phase 1: capture the old a[i+1] for every i. */
#pragma omp parallel for default(none) shared(a, old_a) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            old_a[i] = a[i+1];
        }

        /* Phase 2: original body, reading the saved old a[i+1]. */
#pragma omp parallel for default(none) shared(a, b, c, d, old_a) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * old_a[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(old_a);
    return (real_t)0;
}
