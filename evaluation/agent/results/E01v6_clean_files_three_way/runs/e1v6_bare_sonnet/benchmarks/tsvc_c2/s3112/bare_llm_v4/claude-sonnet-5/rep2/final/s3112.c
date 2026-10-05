#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;

    /* Fixed number of blocks for the parallel prefix-sum (scan).
     * Independent of LEN_1D, so the block arrays below are fixed-size
     * (do not grow with the problem size). */
    int NB = 1024;
    real_t block_sum[1024];
    real_t block_offset[1024];
    int block_size = (LEN_1D + NB - 1) / NB;

    for (int nl = 0; nl < iterations; nl++) {
        /* Phase 1: independent per-block local inclusive scan of a[] into
         * b[], plus each block's total. Blocks don't depend on each other
         * here, so this is safe to run in parallel in any order. */
        #pragma omp parallel for schedule(static) default(none) \
            shared(a, b, block_sum) firstprivate(NB, block_size)
        for (int blk = 0; blk < NB; blk++) {
            int start = blk * block_size;
            int end = start + block_size;
            if (end > LEN_1D) end = LEN_1D;
            if (start > LEN_1D) start = LEN_1D;
            real_t local_sum = (real_t)0.0;
            for (int i = start; i < end; i++) {
                local_sum += a[i];
                b[i] = local_sum;
            }
            block_sum[blk] = local_sum;
        }

        /* Phase 2: sequential exclusive prefix sum over the NB block totals
         * (NB is tiny and constant, so this is negligible work). This moves
         * the cross-block dependence that Phase 1 deferred into a small
         * per-block offset, instead of deleting it. */
        real_t running = (real_t)0.0;
        for (int blk = 0; blk < NB; blk++) {
            block_offset[blk] = running;
            running += block_sum[blk];
        }
        sum = running;

        /* Phase 3: independent per-block application of the offset computed
         * in Phase 2 (which has fully completed, so every block_offset[]
         * entry is final before any thread reads it here). */
        #pragma omp parallel for schedule(static) default(none) \
            shared(b, block_offset) firstprivate(NB, block_size)
        for (int blk = 0; blk < NB; blk++) {
            int start = blk * block_size;
            int end = start + block_size;
            if (end > LEN_1D) end = LEN_1D;
            if (start > LEN_1D) start = LEN_1D;
            real_t off = block_offset[blk];
            for (int i = start; i < end; i++) {
                b[i] += off;
            }
        }

        dummy(a, b, c, d, e);
    }
    return sum;
}
