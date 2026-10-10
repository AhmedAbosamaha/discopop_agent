#include <stdlib.h>
#include "data.h"

#define S341_NB 1024

real_t kernel_s341(void)
{
    const long nb = S341_NB;
    const long bs = ((long)LEN_1D + nb - 1) / nb;
    long *cnt = (long *)malloc(sizeof(long) * nb);
    long *off = (long *)malloc(sizeof(long) * nb);

    for (int nl = 0; nl < iterations; nl++) {
        long blk;

        /* pass 1: count positives per block */
#pragma omp parallel for default(none) shared(b, cnt) firstprivate(nb, bs) schedule(static)
        for (blk = 0; blk < nb; blk++) {
            long lo = blk * bs;
            long hi = lo + bs;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
            long c0 = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) c0++;
            }
            cnt[blk] = c0;
        }

        /* exclusive scan of block counts */
        long run = 0;
        for (long k = 0; k < nb; k++) {
            off[k] = run;
            run += cnt[k];
        }

        /* pass 2: scatter positives to their compacted positions */
#pragma omp parallel for default(none) shared(a, b, off) firstprivate(nb, bs) schedule(static)
        for (blk = 0; blk < nb; blk++) {
            long lo = blk * bs;
            long hi = lo + bs;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
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

    free(cnt);
    free(off);
    return (real_t)0;
}
