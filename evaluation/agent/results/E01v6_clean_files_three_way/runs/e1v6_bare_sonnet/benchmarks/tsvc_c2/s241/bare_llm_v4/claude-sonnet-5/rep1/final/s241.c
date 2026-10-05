#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    /*
     * Original loop:
     *   a[i] = b[i] * c[i] * d[i];
     *   b[i] = a[i] * a[i+1] * d[i];
     *
     * In the sequential version, when iteration i computes b[i] it reads
     * a[i+1] *before* iteration i+1 has run, i.e. it reads the value a[i+1]
     * held at loop entry (from the previous nl pass / initialization), not
     * the value that will be written later in this same pass.  That is a
     * dependence carried between iterations purely through reuse of the
     * array location, not a true data dependence on freshly computed data.
     *
     * To make the iterations independent we snapshot a[] into a heap
     * buffer "aold" before the loop runs, and have each iteration read
     * a[i+1]'s pre-loop value from aold instead of from a[] itself.  Each
     * iteration still writes a[i] and reads/writes b[i] on its own index
     * only, so once aold is populated the i-loop has no cross-iteration
     * dependence left and can run in any order / in parallel.
     */
    real_t *aold = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* aold: snapshot of a[] as it stood before this pass modifies it.
         * Each iteration writes exactly one element -> no race, no need
         * for any data-sharing clause beyond "shared". */
        #pragma omp parallel for shared(a, aold)
        for (int i = 0; i < LEN_1D; i++) {
            aold[i] = a[i];
        }

        /* a, b, c, d, aold are all shared arrays; each iteration i only
         * touches a[i], b[i], c[i], d[i] (written/read by itself alone)
         * and aold[i+1] (read-only, populated above), so iterations are
         * now independent. */
        #pragma omp parallel for shared(a, b, c, d, aold)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * aold[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(aold);
    return (real_t)0;
}
