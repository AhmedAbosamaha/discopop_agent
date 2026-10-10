#include "data.h"

#define S341_NB 256

real_t kernel_s341(void)
{
    long cnt[S341_NB];
    long off[S341_NB];
    const long BS = ((long)LEN_1D + S341_NB - 1) / S341_NB;
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: per-block count of positive b */
        #pragma omp parallel for default(none) shared(b, cnt) firstprivate(BS) schedule(static)
        for (int blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * BS;
            long hi = lo + BS;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
            long c0 = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) c0++;
            }
            cnt[blk] = c0;
        }
        /* exclusive prefix over blocks */
        long s = 0;
        for (int blk = 0; blk < S341_NB; blk++) {
            off[blk] = s;
            s += cnt[blk];
        }
        /* pass 2: compaction with per-block starting offset */
        #pragma omp parallel for default(none) shared(a, b, off) firstprivate(BS) schedule(static)
        for (int blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * BS;
            long hi = lo + BS;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
            long jj = off[blk] - 1;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    jj++;
                    a[jj] = b[i];
                }
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
