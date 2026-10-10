#include "data.h"

#define S341_NCHUNKS 256

real_t kernel_s341(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Per-chunk element counts and exclusive offsets. Fixed-size
         * (does not grow with LEN_1D), so stack storage is fine. */
        int chunk_count[S341_NCHUNKS];
        int chunk_offset[S341_NCHUNKS];
        int chunk_size = (LEN_1D + S341_NCHUNKS - 1) / S341_NCHUNKS;

        /* Pass 1: each chunk independently counts how many elements of
         * b[] in its own range satisfy b[i] > 0.  chunk_count[blk] is
         * written only by iteration blk, so chunks have no dependence
         * on each other. start/end/cnt/i are declared inside the loop
         * body, so they are private per iteration automatically. */
        #pragma omp parallel for default(none) \
            shared(b, chunk_count, chunk_size) schedule(static)
        for (int blk = 0; blk < S341_NCHUNKS; blk++) {
            int start = blk * chunk_size;
            int end = start + chunk_size;
            if (start > LEN_1D) start = LEN_1D;
            if (end > LEN_1D) end = LEN_1D;
            int cnt = 0;
            for (int i = start; i < end; i++) {
                if (b[i] > (real_t)0.) cnt++;
            }
            chunk_count[blk] = cnt;
        }

        /* Sequential exclusive prefix sum over the small, fixed-size
         * per-chunk counts (O(S341_NCHUNKS), not O(LEN_1D)).  This is
         * the only place the original running index "j" still moves
         * between iterations; it now moves between chunks instead of
         * between individual elements. */
        int running = 0;
        for (int blk = 0; blk < S341_NCHUNKS; blk++) {
            chunk_offset[blk] = running;
            running += chunk_count[blk];
        }

        /* Pass 2: every chunk knows exactly where its first qualifying
         * element belongs in a[], so chunks pack their own elements into
         * disjoint, non-overlapping ranges of a[] concurrently, in the
         * same left-to-right order as the original serial loop. */
        #pragma omp parallel for default(none) \
            shared(a, b, chunk_offset, chunk_size) schedule(static)
        for (int blk = 0; blk < S341_NCHUNKS; blk++) {
            int start = blk * chunk_size;
            int end = start + chunk_size;
            if (start > LEN_1D) start = LEN_1D;
            if (end > LEN_1D) end = LEN_1D;
            int j = chunk_offset[blk] - 1;
            for (int i = start; i < end; i++) {
                if (b[i] > (real_t)0.) {
                    j++;
                    a[j] = b[i];
                }
            }
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
