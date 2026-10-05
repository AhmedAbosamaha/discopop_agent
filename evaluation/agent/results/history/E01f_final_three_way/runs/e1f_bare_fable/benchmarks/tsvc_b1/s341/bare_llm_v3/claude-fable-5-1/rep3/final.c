/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"
#include <stdlib.h>

/* Between two repetitions a few INPUT elements change, so no repetition can be skipped,
 * merged with another or run out of order: the repetition loop is sequential by a true
 * dependence, and the loop under study is the one inside it. */
static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

static real_t kernel_s341(void)
{
    int j;
    /* Stream compaction as a block-wise prefix sum: count positives per block in
     * parallel, scan the block counts sequentially, then pack each block in parallel
     * starting at its own offset.  Every a[] slot is written by exactly one block. */
    const int nb = 512;                              /* number of blocks */
    const int bs = (LEN_1D + nb - 1) / nb;           /* elements per block */
    int *cnt = (int *)malloc((size_t)nb * sizeof(int));
    for (int nl = 0; nl < R; nl++) {
        /* phase 1: per-block count of positive b[i] */
        #pragma omp parallel for shared(b, cnt) firstprivate(bs, nb)
        for (int blk = 0; blk < nb; blk++) {
            int lo = blk * bs;
            int hi = lo + bs;
            if (hi > LEN_1D) hi = LEN_1D;
            int c = 0;
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    c++;
                }
            }
            cnt[blk] = c;
        }
        /* phase 2: exclusive scan -> cnt[blk] = first output index of block blk;
         * j ends as (total positives - 1), the same value the original loop leaves. */
        j = -1;
        for (int blk = 0; blk < nb; blk++) {
            int c = cnt[blk];
            cnt[blk] = j + 1;
            j += c;
        }
        /* phase 3: pack each block into a[] from its own offset */
        #pragma omp parallel for shared(a, b, cnt) firstprivate(bs, nb)
        for (int blk = 0; blk < nb; blk++) {
            int lo = blk * bs;
            int hi = lo + bs;
            if (hi > LEN_1D) hi = LEN_1D;
            int k = cnt[blk];
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[k] = b[i];
                    k++;
                }
            }
        }
        pb_mix(nl);
    }
    free(cnt);
    return (real_t)0;
}

PB_MAIN(kernel_s341)
