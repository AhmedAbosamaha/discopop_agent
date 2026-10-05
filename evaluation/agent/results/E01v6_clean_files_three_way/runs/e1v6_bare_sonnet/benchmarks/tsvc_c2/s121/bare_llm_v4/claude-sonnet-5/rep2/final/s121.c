#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s121(void)
{
    /* a_old holds a snapshot of a[] taken before each sweep, so the
     * parallel loop below only ever reads "old" values (breaking the
     * anti-dependence between a[i] (write) and a[i+1] (read)) while
     * writing to disjoint indices of a[]. Heap-allocated since its size
     * (LEN_1D) grows with the problem. */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_old, a, sizeof(real_t) * (size_t)LEN_1D);

        /* a: shared, written at a unique index i per iteration -> no
         *    write-write or write-read conflicts across iterations.
         * b: shared, read-only.
         * a_old: shared, read-only snapshot taken above; using it instead
         *    of a[] removes the cross-iteration dependence entirely.
         * i: loop variable, implicitly private to each iteration. */
        #pragma omp parallel for default(none) shared(a, b, a_old) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_old[i+1] + b[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
