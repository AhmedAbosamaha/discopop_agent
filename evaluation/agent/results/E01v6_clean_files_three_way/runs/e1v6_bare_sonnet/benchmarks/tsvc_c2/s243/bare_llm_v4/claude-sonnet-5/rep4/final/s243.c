#include "data.h"
#include <stdlib.h>

real_t kernel_s243(void)
{
    /* Heap-allocated snapshot of a[] taken before each inner sweep, so
       that the read of a[i+1] inside the sweep sees the pre-sweep value
       (matching the original sequential execution order) instead of a
       value possibly already overwritten by another, concurrently
       running iteration. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot a[] so the compute loop below can run its iterations
           in any order/parallel without racing on a[i+1]. */
        #pragma omp parallel for default(none) shared(a, a_old)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        #pragma omp parallel for default(none) shared(a, b, c, d, e, a_old)
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
