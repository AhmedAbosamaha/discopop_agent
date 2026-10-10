#include "data.h"
#include <stdlib.h>
#ifdef _OPENMP
#include <omp.h>
#endif

real_t kernel_s341(void)
{
    int j;

    /* Stream-compaction loop: the original keeps a running counter j that
     * is incremented whenever b[i] > 0, and writes a[j] = b[i]. The target
     * index for each positive element is "how many positive elements
     * occurred at or before i" -- a value dependence that must flow in
     * order. We move that dependence from a per-element O(LEN_1D) chain
     * down to a per-block O(numBlocks) chain:
     *
     *   localRank[i]   : for a positive b[i], its 0-based rank among the
     *                    positive elements within its own block (filled by
     *                    an independent, purely local, serial scan per
     *                    block -- blocks can run in parallel).
     *   blockCount[k]  : number of positive elements found in block k.
     *   blockOffset[k] : exclusive prefix sum of blockCount -- number of
     *                    positive elements in all blocks before k.
     *
     * The final index for a positive b[i] in block k is
     *   blockOffset[k] + localRank[i]
     * which equals exactly the same j the sequential version would have
     * produced, so a[] ends up byte-identical.
     */
    int numBlocks = 1;
#ifdef _OPENMP
    numBlocks = omp_get_max_threads() * 4;
#endif
    if (numBlocks > LEN_1D) numBlocks = LEN_1D;
    if (numBlocks < 1) numBlocks = 1;

    int *localRank = (int *)malloc(sizeof(int) * LEN_1D);
    int *blockCount = (int *)malloc(sizeof(int) * numBlocks);
    int *blockOffset = (int *)malloc(sizeof(int) * numBlocks);

    int blockSize = (LEN_1D + numBlocks - 1) / numBlocks;

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: each block independently scans its own range of b[],
         * computing local ranks and the block's total positive count.
         * Disjoint index ranges per block -> race-free. */
        #pragma omp parallel for schedule(static) \
            shared(b, localRank, blockCount, blockSize, numBlocks)
        for (int blk = 0; blk < numBlocks; blk++) {
            int start = blk * blockSize;
            int end = start + blockSize;
            if (end > LEN_1D) end = LEN_1D;
            int cnt = -1;
            for (int i = start; i < end; i++) {
                if (b[i] > (real_t)0.) {
                    cnt++;
                    localRank[i] = cnt;
                }
            }
            blockCount[blk] = cnt + 1;
        }

        /* Pass 2: sequential exclusive prefix sum over the (small) number
         * of blocks -- this is the only part of the original cross-
         * iteration dependence that survives, now shrunk to O(numBlocks). */
        int running = 0;
        for (int blk = 0; blk < numBlocks; blk++) {
            blockOffset[blk] = running;
            running += blockCount[blk];
        }
        j = running - 1;

        /* Pass 3: each block writes its positive elements to their final
         * compacted position in a[]. Offsets are an exclusive prefix sum
         * and ranks are unique within a block, so every write target
         * across all blocks is distinct -> race-free. */
        #pragma omp parallel for schedule(static) \
            shared(a, b, localRank, blockOffset, blockSize, numBlocks)
        for (int blk = 0; blk < numBlocks; blk++) {
            int start = blk * blockSize;
            int end = start + blockSize;
            if (end > LEN_1D) end = LEN_1D;
            int off = blockOffset[blk];
            for (int i = start; i < end; i++) {
                if (b[i] > (real_t)0.) {
                    a[off + localRank[i]] = b[i];
                }
            }
        }

        dummy(a, b, c, d, e);
    }

    free(localRank);
    free(blockCount);
    free(blockOffset);

    return (real_t)0;
}
