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

#include <stdlib.h>

/* Fixed block length for the blocked prefix scan: independent of the thread
 * count so that the association of the partial sums is the same in every run. */
#define S3112_BS 1024L

static real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    long n = (long)LEN_1D;
    long nblk = (n + S3112_BS - 1) / S3112_BS;
    real_t *bsum = (real_t *)malloc((size_t)nblk * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        /* pass 1: partial sum of every block (blocks are independent) */
        #pragma omp parallel for schedule(static) shared(a, bsum) firstprivate(n, nblk)
        for (long blk = 0; blk < nblk; blk++) {
            long lo = blk * S3112_BS;
            long hi = lo + S3112_BS;
            if (hi > n) hi = n;
            real_t s = (real_t)0.0;
            for (long i = lo; i < hi; i++) {
                s += a[i];
            }
            bsum[blk] = s;
        }
        /* pass 2: exclusive prefix over the block sums (sequential, nblk entries) */
        real_t carry = (real_t)0.0;
        for (long blk = 0; blk < nblk; blk++) {
            real_t t = bsum[blk];
            bsum[blk] = carry;
            carry += t;
        }
        /* pass 3: each block re-runs the original running-sum chain from its offset */
        #pragma omp parallel for schedule(static) shared(a, b, bsum) firstprivate(n, nblk)
        for (long blk = 0; blk < nblk; blk++) {
            long lo = blk * S3112_BS;
            long hi = lo + S3112_BS;
            if (hi > n) hi = n;
            real_t s = bsum[blk];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }
        sum = b[n - 1];
        pb_mix(nl);
    }
    free(bsum);
    return sum;
}

PB_MAIN(kernel_s3112)
