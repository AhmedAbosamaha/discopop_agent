#include <stdlib.h>
#include "data.h"

/* number of independent blocks used for the two-pass (count / scatter) compaction */
#define S341_NB 512

real_t kernel_s341(void)
{
    int j;
    int *blockcnt = (int *)malloc((S341_NB + 1) * sizeof(int));
    const int chunk = (LEN_1D + S341_NB - 1) / S341_NB;

    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: count positive entries of b in each block */
        #pragma omp parallel for schedule(static) firstprivate(chunk) shared(blockcnt, b)
        for (int blk = 0; blk < S341_NB; blk++) {
            int lo = blk * chunk;
            int hi = lo + chunk;
            int cnt = 0;
            if (hi > LEN_1D) hi = LEN_1D;
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    cnt++;
                }
            }
            blockcnt[blk] = cnt;
        }

        /* exclusive scan over block counts: starting offset of each block in a */
        int total = 0;
        for (int blk = 0; blk < S341_NB; blk++) {
            int c0 = blockcnt[blk];
            blockcnt[blk] = total;
            total += c0;
        }
        blockcnt[S341_NB] = total;

        /* pass 2: scatter, each block writes its own disjoint range of a */
        #pragma omp parallel for schedule(static) firstprivate(chunk) shared(blockcnt, a, b)
        for (int blk = 0; blk < S341_NB; blk++) {
            int lo = blk * chunk;
            int hi = lo + chunk;
            int pos = blockcnt[blk];
            if (hi > LEN_1D) hi = LEN_1D;
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[pos] = b[i];
                    pos++;
                }
            }
        }

        j = total - 1;
        dummy(a, b, c, d, e);
    }

    free(blockcnt);
    (void)j;
    return (real_t)0;
}
