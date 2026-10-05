#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    /* idx[i] will hold, for each i, an exclusive prefix count of how many
     * earlier elements satisfy b[i] > 0. For an i where the predicate is
     * true, this value equals exactly the destination index the original
     * sequential code would have assigned via its running counter j.
     * Heap-allocated because LEN_1D can be very large. */
    int *idx = (int *)malloc((size_t)LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: mark which elements satisfy the predicate. Each
         * iteration only reads b[i] and writes its own idx[i] -- fully
         * independent, no dependence between iterations. */
        #pragma omp parallel for default(none) shared(b, idx) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            idx[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Pass 2: sequential exclusive prefix sum over the flags. This is
         * the one genuinely sequential piece of the dependence (a running
         * count), but it is cheap integer bookkeeping, not the original
         * real_t compare-and-copy work, and it stays O(n), not O(n^2). */
        int run = 0;
        for (int i = 0; i < LEN_1D; i++) {
            int t = idx[i];
            idx[i] = run;
            run += t;
        }

        /* Pass 3: scatter. Re-testing the predicate is cheap duplicate
         * work (constant factor), not a growing recomputation. Because
         * idx[i] is a strictly increasing count across true predicates,
         * every write target a[idx[i]] is unique across iterations, so
         * this loop is race-free despite writing through a computed
         * index. */
        #pragma omp parallel for default(none) shared(a, b, idx) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[idx[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(idx);
    return (real_t)0;
}
