#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    /* Heap-allocated snapshot buffer: holds the pre-update values of a[]
     * so that the parallel update loop can read the "old" a[i+1] that the
     * original sequential loop would have seen (since in the original,
     * a[i+1] is only overwritten by a later iteration, after b[i] already
     * used its old value). Sized LEN_1D (problem-size dependent), so it
     * must be malloc'd, not a local array. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot current a[] before this pass updates it in place.
         * Iterations are fully independent element-wise copies. */
        #pragma omp parallel for shared(a, a_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        /* a[i] depends only on old b[i],c[i],d[i] (all shared, read-only
         * per i). b[i] depends on the freshly computed a[i] (same
         * iteration, safe) and a_old[i+1] (snapshot taken above, so no
         * dependence on another iteration's write to a[]). This removes
         * the original loop-carried dependence entirely. */
        #pragma omp parallel for shared(a, b, c, d, a_old) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
