#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    /* Snapshot buffer holding the pre-sweep values of a[]. Heap-allocated
     * since its size scales with LEN_1D; allocated once and reused across
     * the `iterations` sweeps so the extra work stays O(n) per sweep,
     * matching the original cost, instead of growing with iterations. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Capture the values a[] holds before this sweep mutates them.
         * Each iteration touches a distinct index of a_old/a: independent. */
        #pragma omp parallel for default(none) shared(a, a_old)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        /* Original dependence: a[i] = a[i+1] + b[i] only ever used the
         * value a[i+1] had BEFORE this sweep (in sequential order, index
         * i+1 is written later, at iteration i+1, so the read at iteration
         * i always saw the old value). Reading that frozen value from
         * a_old (read-only, shared) and writing the distinct index a[i]
         * (shared, no overlap between iterations) reproduces that exact
         * data flow with no dependence between iterations, so the
         * iterations may run in any order/thread. */
        #pragma omp parallel for default(none) shared(a, a_old, b)
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;
            a[i] = a_old[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
