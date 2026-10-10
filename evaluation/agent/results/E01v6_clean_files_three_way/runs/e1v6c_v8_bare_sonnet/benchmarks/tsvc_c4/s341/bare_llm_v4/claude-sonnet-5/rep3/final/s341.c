#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    /* Heap-allocated scratch buffer: holds, per element, first the
       0/1 "selected" flag and then (after the scan) the exclusive
       prefix-sum destination index for that element. Sized LEN_1D,
       which grows with the problem, so it must not be a stack array. */
    int *pos = (int *)malloc((size_t)LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: independent per-i flag computation, fully parallel.
           b is read-only here; pos[i] is written only by iteration i. */
        #pragma omp parallel for default(none) shared(b, pos)
        for (int i = 0; i < LEN_1D; i++) {
            pos[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Pass 2: serial exclusive prefix sum. This is the only part of
           the original loop-carried dependence that remains, and it is
           O(n), the same order as the original loop, not O(n^2). It
           turns pos[i] into the exact destination index that element i
           would have received under the original sequential compaction
           order. */
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            int f = pos[i];
            pos[i] = count;
            count += f;
        }
        j = count - 1;

        /* Pass 3: independent scatter. b is unchanged since pass 1 (it is
           only mutated by dummy(), called after this loop), so re-testing
           the condition here is safe and deterministic. Because pos[i] is
           a strictly increasing sequence over the indices that satisfy the
           condition, each selected i writes a distinct a[] slot: no two
           iterations ever write the same location. */
        #pragma omp parallel for default(none) shared(a, b, pos)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[pos[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(pos);
    (void)j;
    return (real_t)0;
}
