#include "data.h"
#include <stdlib.h>

real_t kernel_s243(void)
{
    /* The original loop body's third statement reads a[i+1] before that
     * slot has been overwritten by iteration i+1 (which runs later in the
     * sequential order).  To let the iterations run in any order/parallel,
     * we snapshot a[] into a heap-allocated buffer (a_old) before the
     * per-i updates of this nl iteration begin, and read a[i+1] from that
     * snapshot instead of from the live, concurrently-written array.  The
     * snapshot must be heap-allocated (LEN_1D can be very large) and must
     * be refreshed every nl iteration because dummy() mutates a[] in
     * between iterations. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot a[] as it stands before this iteration's updates.
         * Each i writes only a_old[i]; no cross-iteration dependence. */
        #pragma omp parallel for default(none) shared(a, a_old)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        /* Each i now writes only a[i] and b[i], and reads a_old[i+1]
         * (the pre-update snapshot) instead of the live a[i+1], removing
         * the dependence between iterations. b, c, d, e are read-only
         * here except for b[i]/a[i] which are each written by exactly one
         * iteration, so the arrays can stay shared. */
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
