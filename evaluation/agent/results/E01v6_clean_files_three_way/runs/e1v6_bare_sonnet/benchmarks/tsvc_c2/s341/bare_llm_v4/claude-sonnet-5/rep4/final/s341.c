#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    /* pos[i] holds the exclusive prefix count of elements with b[i] > 0
     * seen at indices < i.  It replaces the sequentially-carried counter
     * "j" from the original code: once pos[] is fully computed, every
     * matching element already knows its final slot in a[], so the
     * write-out loop can run with independent iterations. Heap-allocated
     * since LEN_1D can be very large. */
    int *pos = (int *)malloc((size_t)LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        int count = 0; /* scan reduction variable: running exclusive prefix sum */

        /* Pass 1: exclusive prefix sum of "b[i] > 0" into pos[].
         * b   : shared, read-only.
         * pos : shared, each i writes a distinct element -> no race.
         * count: scan (inscan) reduction variable, maintained correctly
         *        across threads by the OpenMP scan construct; its final
         *        value is not needed after the loop. */
        #pragma omp parallel for reduction(inscan, +:count) shared(b, pos)
        for (int i = 0; i < LEN_1D; i++) {
            pos[i] = count;
            #pragma omp scan exclusive(count)
            count += (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Pass 2: scatter matching elements to their precomputed slot.
         * a, b, pos: shared; pos[] is a strictly increasing injective map
         * over the matching indices, so distinct iterations that write
         * write to distinct locations in a[] -> no race. */
        #pragma omp parallel for shared(a, b, pos)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[pos[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(pos);
    return (real_t)0;
}
