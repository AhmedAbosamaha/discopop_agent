/* TSVC-2 loop s3112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s3112.h"

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

#define SCAN_NBLK 64

static real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    real_t bsum[SCAN_NBLK];
    real_t boff[SCAN_NBLK];
    const long n = (long)LEN_1D;
    const long bs = (n + SCAN_NBLK - 1) / SCAN_NBLK;
    int blk;
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: per-block local sums */
#pragma omp parallel for shared(bsum) firstprivate(n, bs) schedule(static)
        for (blk = 0; blk < SCAN_NBLK; blk++) {
            long lo = (long)blk * bs;
            long hi = lo + bs;
            if (hi > n) hi = n;
            real_t s = (real_t)0.0;
            for (long i = lo; i < hi; i++)
                s += a[i];
            bsum[blk] = s;
        }
        /* serial exclusive scan over block sums */
        {
            real_t run = (real_t)0.0;
            for (int j = 0; j < SCAN_NBLK; j++) {
                boff[j] = run;
                run += bsum[j];
            }
        }
        /* pass 2: per-block running sums from the block's offset */
#pragma omp parallel for shared(boff) firstprivate(n, bs) schedule(static)
        for (blk = 0; blk < SCAN_NBLK; blk++) {
            long lo = (long)blk * bs;
            long hi = lo + bs;
            if (hi > n) hi = n;
            real_t s = boff[blk];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }
        sum = b[LEN_1D - 1];
        pb_mix(nl);
    }
    return sum;
}

PB_MAIN(kernel_s3112)
