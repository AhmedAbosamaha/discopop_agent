#include "data.h"
#include <stdlib.h>

/* Fixed number of scan blocks used to break the i-1 -> i recurrence below
 * into independent chunks. Independent of LEN_1D, so the extra blockSum
 * buffer is O(1) per activation, not O(n). */
#define S323_NUM_BLOCKS 1024

real_t kernel_s323(void)
{
    const int n = LEN_1D - 1;                 /* number of recurrence elements: i = 1..LEN_1D-1 */
    const int NB = (n > 0) ? S323_NUM_BLOCKS : 1;
    const int blockSize = (n > 0) ? (n + NB - 1) / NB : 1;
    /* Per-block running totals / exclusive prefixes. Heap-allocated because
     * its size must not live on the stack for large LEN_1D runs (even
     * though here it is O(NB), a compile-time constant, not O(n)). */
    real_t *blockSum = (real_t *)malloc((size_t)NB * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        if (n > 0) {
            /* b[0] is never written inside the i=1..LEN_1D-1 loop, so it is
             * the fixed base value the whole recurrence starts from. */
            const real_t b0 = b[0];

            /* Pass 1: for each block, replay the same two-step recurrence
             * that the original loop performs (a = rb + c*d; rb = a + c*e)
             * over the block's own index range, starting from rb = 0.
             * Blocks do not read or write each other's data -> independent
             * iterations. The final rb per block is that block's local
             * contribution to the overall running sum. */
            #pragma omp parallel for schedule(static) default(none) \
                shared(c, d, e, blockSum, blockSize, n) firstprivate(NB)
            for (int blk = 0; blk < NB; blk++) {
                int start = 1 + blk * blockSize;
                int end = start + blockSize;
                if (start > n + 1) start = n + 1;
                if (end > n + 1) end = n + 1;
                real_t rb = (real_t)0;
                for (int i = start; i < end; i++) {
                    real_t ai = rb + c[i] * d[i];
                    rb = ai + c[i] * e[i];
                }
                blockSum[blk] = rb;
            }

            /* Sequential exclusive scan over the NB block totals (NB is a
             * fixed constant, so this is O(1) extra work per activation,
             * not O(n)). blockSum[blk] becomes the true running b-value
             * contributed by all blocks before blk. */
            real_t running = (real_t)0;
            for (int blk = 0; blk < NB; blk++) {
                real_t s = blockSum[blk];
                blockSum[blk] = running;
                running += s;
            }

            /* Pass 2: replay the recurrence once more per block, now seeded
             * with the real running value entering that block
             * (b0 + exclusive prefix of earlier blocks), and store the
             * actual results into a[] and b[]. The only cross-block
             * dependence (the running b value) was already resolved above,
             * so blocks are independent here too: each writes only its own
             * disjoint range of a[] and b[]. */
            #pragma omp parallel for schedule(static) default(none) \
                shared(a, b, c, d, e, blockSum, blockSize, n, b0) firstprivate(NB)
            for (int blk = 0; blk < NB; blk++) {
                int start = 1 + blk * blockSize;
                int end = start + blockSize;
                if (start > n + 1) start = n + 1;
                if (end > n + 1) end = n + 1;
                real_t rb = b0 + blockSum[blk];
                for (int i = start; i < end; i++) {
                    a[i] = rb + c[i] * d[i];
                    rb = a[i] + c[i] * e[i];
                    b[i] = rb;
                }
            }
        }
        dummy(a, b, c, d, e);
    }

    free(blockSum);
    return (real_t)0;
}
