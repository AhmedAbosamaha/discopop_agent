#include "data.h"
#include <stdlib.h>

real_t kernel_s211(void)
{
    /* Heap-allocated snapshot of b, used to break the i-1/i+1 recurrence
     * on b within a single nl iteration. Allocated once; size tracks the
     * (possibly large) problem size LEN_1D, so it must live on the heap. */
    real_t *bold = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot b's current values before this iteration's updates.
         * Independent, embarrassingly parallel copy. */
        #pragma omp parallel for default(none) shared(b, bold) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            bold[i] = b[i];
        }

        /* Both a[i] and b[i] now read only from the read-only snapshot
         * bold (plus c, d, e) and write only their own a[i]/b[i], so
         * iterations no longer depend on each other and can run in any
         * order. */
        #pragma omp parallel for default(none) shared(a, b, bold, c, d, e) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = bold[i - 1] + c[i] * d[i];
            b[i] = bold[i + 1] - e[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(bold);
    return (real_t)0;
}
