#include "data.h"

#define S341_NB 256

real_t kernel_s341(void)
{
    long cnt[S341_NB];
    long start[S341_NB];
    const long chunk = ((long)LEN_1D + S341_NB - 1) / S341_NB;
    int blk;
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: count positives per block */
        #pragma omp parallel for default(none) shared(cnt, b) firstprivate(chunk) schedule(static)
        for (blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * chunk;
            long hi = lo + chunk;
            if (hi > LEN_1D) hi = LEN_1D;
            long n = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) n++;
            }
            cnt[blk] = n;
        }
        /* exclusive scan: starting j for each block */
        long run = 0;
        for (int k = 0; k < S341_NB; k++) {
            start[k] = run;
            run += cnt[k];
        }
        /* pass 2: pack each block into its own output range */
        #pragma omp parallel for default(none) shared(start, a, b) firstprivate(chunk) schedule(static)
        for (blk = 0; blk < S341_NB; blk++) {
            long lo = (long)blk * chunk;
            long hi = lo + chunk;
            if (hi > LEN_1D) hi = LEN_1D;
            long j = start[blk];
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
