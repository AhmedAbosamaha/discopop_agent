#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    /* Heap-allocated snapshot of a[] so the update loop can read the
     * pre-update values without an anti-dependence between iterations. */
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot: each i reads a[i] and writes tmp[i] -- disjoint
         * per-iteration locations, fully independent. */
        #pragma omp parallel for shared(a, tmp) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            tmp[i] = a[i];
        }

        /* Update: reads come only from the untouched snapshot tmp[],
         * writes go only to a[i] (unique per iteration), so the former
         * anti-dependence (a[i+1] read here, written by a later
         * iteration) no longer exists. j is declared inside the loop
         * body, so it is already private to each iteration. */
        #pragma omp parallel for shared(a, b, tmp) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;
            a[i] = tmp[j] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(tmp);
    return (real_t)0;
}
