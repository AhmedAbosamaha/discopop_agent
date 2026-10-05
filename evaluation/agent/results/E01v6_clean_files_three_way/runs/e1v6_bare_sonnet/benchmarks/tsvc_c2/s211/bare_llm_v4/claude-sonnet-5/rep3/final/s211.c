#include "data.h"
#include <stdlib.h>

real_t kernel_s211(void)
{
    /* newb[i] holds the "new" b[i] value (as produced by the original
     * sequential loop) before it is written back into b[].  Heap-allocated
     * because LEN_1D can be very large. */
    real_t *newb = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: compute the new b[i] values from the OLD b[] only.
         * b[i+1] here is never written by this loop (only indices
         * 1..LEN_1D-2 are ever written), so every iteration reads
         * untouched data and writes its own distinct newb[i] slot:
         * fully independent. */
        #pragma omp parallel for default(none) shared(b, c, d, e, newb) schedule(static)
        for (int i = 1; i < LEN_1D - 1; i++) {
            newb[i] = b[i + 1] - e[i] * d[i];
        }

        /* Pass 2: compute a[i] from the "new" b[i-1] value, matching what
         * the original sequential loop would have already written to
         * b[i-1] by the time it computed a[i].  For i==1, b[0] is never
         * written by the loop, so the original (untouched) b[0] is used
         * directly.  Each iteration writes its own a[i]: independent. */
        #pragma omp parallel for default(none) shared(a, b, c, d, newb) schedule(static)
        for (int i = 1; i < LEN_1D - 1; i++) {
            real_t bprev = (i == 1) ? b[0] : newb[i - 1];
            a[i] = bprev + c[i] * d[i];
        }

        /* Pass 3: publish the new b[] values so dummy() and the next nl
         * iteration observe the same final state as the original code.
         * Independent per-index writes. */
        #pragma omp parallel for default(none) shared(b, newb) schedule(static)
        for (int i = 1; i < LEN_1D - 1; i++) {
            b[i] = newb[i];
        }

        dummy(a, b, c, d, e);
    }

    free(newb);
    return (real_t)0;
}
