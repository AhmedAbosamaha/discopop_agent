/* TSVC-2 loop s341, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s341.h"

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
    enum { NB = 256 };          /* fixed number of blocks, independent of LEN_1D */
    long cnt[NB];
    for (int nl = 0; nl < R; nl++) {
        long chunk = ((long)LEN_1D + NB - 1) / NB;

        /* pass 1: number of positive b[] in each block */
#pragma omp parallel for firstprivate(chunk) shared(cnt)
        for (int blk = 0; blk < NB; blk++) {
            long lo = (long)blk * chunk;
            long hi = lo + chunk;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
            long c = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    c++;
                }
            }
            cnt[blk] = c;
        }

        /* exclusive scan: cnt[blk] becomes the output offset where block blk starts */
        long run = 0;
        for (int blk = 0; blk < NB; blk++) {
            long t = cnt[blk];
            cnt[blk] = run;
            run += t;
        }

        /* pass 2: pack each block into its own disjoint range of a[] */
#pragma omp parallel for firstprivate(chunk) shared(cnt)
        for (int blk = 0; blk < NB; blk++) {
            long lo = (long)blk * chunk;
            long hi = lo + chunk;
            if (hi > (long)LEN_1D) hi = (long)LEN_1D;
            long jj = cnt[blk] - 1;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    jj++;
                    a[jj] = b[i];
                }
            }
        }

        j = (int)run - 1;
        pb_mix(nl);
    }
    (void)j;
    return (real_t)0;
}

PB_MAIN(kernel_s341)
