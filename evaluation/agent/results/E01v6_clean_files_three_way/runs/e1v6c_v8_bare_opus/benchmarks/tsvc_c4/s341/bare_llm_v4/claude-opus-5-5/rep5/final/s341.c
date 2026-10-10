#include "data.h"

#define S341_NB 256

real_t kernel_s341(void)
{
    long cnt[S341_NB];
    long off[S341_NB];
    const long bs = ((long)LEN_1D + S341_NB - 1) / S341_NB;
    int blk;
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: count positives per block */
        #pragma omp parallel for default(none) shared(b, cnt) firstprivate(bs) schedule(static)
        for (blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * bs;
            long hi = lo + bs;
            if (hi > LEN_1D) hi = LEN_1D;
            long c0 = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) c0++;
            }
            cnt[blk] = c0;
        }
        /* exclusive scan of block counts (serial, O(NB)) */
        long run = 0;
        for (int k = 0; k < S341_NB; k++) {
            off[k] = run;
            run += cnt[k];
        }
        /* pass 2: scatter into a at precomputed offsets */
        #pragma omp parallel for default(none) shared(a, b, off) firstprivate(bs) schedule(static)
        for (blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * bs;
            long hi = lo + bs;
            if (hi > LEN_1D) hi = LEN_1D;
            long j = off[blk];
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[j] = b[i];
                    j++;
                }
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
