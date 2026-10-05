#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    /* Heap-allocated snapshot of a[]'s pre-update values. Needed because the
     * original loop's computation of b[i] reads a[i+1] *before* it has been
     * multiplied by c[i+1] (that happens at the next iteration). Taking a
     * read-only snapshot removes the cross-iteration dependence entirely. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
#pragma omp parallel for default(none) shared(a, a_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }
#pragma omp parallel for default(none) shared(a, b, c, d, a_old) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_old[i] * c[i];
            b[i] += a_old[i + 1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
