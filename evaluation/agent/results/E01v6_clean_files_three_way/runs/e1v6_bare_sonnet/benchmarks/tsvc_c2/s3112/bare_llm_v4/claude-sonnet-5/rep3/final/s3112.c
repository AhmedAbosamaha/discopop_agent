#include "data.h"
#include <stdlib.h>
#if defined(_OPENMP)
#include <omp.h>
#endif

real_t kernel_s3112(void)
{
    real_t sum;

    /* The inner recurrence (b[i] = sum of a[0..i]) carries a true value
     * dependence across i, so it is restructured as a two-pass block scan:
     *   pass 1: each block independently computes its own local prefix sum
     *            into b[] and records its block total (parallel, disjoint
     *            index ranges per block -> no race)
     *   scan:    a short SEQUENTIAL exclusive prefix scan over the (few)
     *            block totals -- this carries the dependence between
     *            blocks that the original loop carried between elements
     *   pass 2: each block adds its now-known prefix offset to its
     *            elements of b[] (parallel, disjoint ranges per block)
     *
     * nblocks is sized from the thread count (not from LEN_1D) so the
     * sequential scan stays O(threads), negligible next to the O(LEN_1D)
     * parallel work, while still giving enough blocks per thread to
     * balance load. */
    int nthreads = 1;
#if defined(_OPENMP)
    nthreads = omp_get_max_threads();
#endif
    int nblocks = nthreads * 8;
    if (nblocks > LEN_1D) nblocks = LEN_1D;
    if (nblocks < 1) nblocks = 1;

    int block_size = (LEN_1D + nblocks - 1) / nblocks;
    /* Recompute the exact block count for this block_size so start/end
     * computed from (blk, block_size) always stay within [0, LEN_1D]. */
    nblocks = (LEN_1D + block_size - 1) / block_size;

    real_t *blockSum = (real_t *)malloc((size_t)nblocks * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: independent per-block local prefix sums + block totals. */
        #pragma omp parallel for schedule(static) default(none) \
            shared(a, b, blockSum, nblocks, block_size)
        for (int blk = 0; blk < nblocks; blk++) {
            int start = blk * block_size;
            int end = start + block_size;
            if (end > LEN_1D) end = LEN_1D;
            real_t s = (real_t)0.0;
            for (int i = start; i < end; i++) {
                s += a[i];
                b[i] = s;
            }
            blockSum[blk] = s;
        }

        /* Sequential exclusive prefix scan over the block totals: carries
         * the cross-block dependence. O(nblocks), not O(LEN_1D). */
        real_t running = (real_t)0.0;
        for (int blk = 0; blk < nblocks; blk++) {
            real_t total = blockSum[blk];
            blockSum[blk] = running;
            running += total;
        }
        sum = running;

        /* Pass 2: add each block's now-known offset to its elements. */
        #pragma omp parallel for schedule(static) default(none) \
            shared(b, blockSum, nblocks, block_size)
        for (int blk = 0; blk < nblocks; blk++) {
            real_t offset = blockSum[blk];
            int start = blk * block_size;
            int end = start + block_size;
            if (end > LEN_1D) end = LEN_1D;
            for (int i = start; i < end; i++) {
                b[i] += offset;
            }
        }

        dummy(a, b, c, d, e);
    }

    free(blockSum);
    return sum;
}
