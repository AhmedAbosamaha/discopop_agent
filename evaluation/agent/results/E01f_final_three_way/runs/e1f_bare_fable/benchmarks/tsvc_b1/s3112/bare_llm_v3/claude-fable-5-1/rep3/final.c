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

#define S3112_MAX_BLOCKS 512

static real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    /* Fixed, bounded number of blocks: scratch does not grow with LEN_1D. */
    const int nb = (LEN_1D < S3112_MAX_BLOCKS) ? (int)LEN_1D : S3112_MAX_BLOCKS;
    real_t bs[S3112_MAX_BLOCKS];

    for (int nl = 0; nl < R; nl++) {
        sum = (real_t)0.0;

        /* Pass 1: per-block partial sums, each block starting from zero. */
#pragma omp parallel for schedule(static) shared(a, bs, nb)
        for (int j = 0; j < nb; j++) {
            long lo = ((long)LEN_1D * j) / nb;
            long hi = ((long)LEN_1D * (j + 1)) / nb;
            real_t s = (real_t)0.0;
            for (long i = lo; i < hi; i++) {
                s += a[i];
            }
            bs[j] = s;
        }

        /* Sequential carry pass over the (few) blocks: bs[j] becomes the
         * running sum carried into block j. */
        {
            real_t run = (real_t)0.0;
            for (int j = 0; j < nb; j++) {
                real_t t = bs[j];
                bs[j] = run;
                run += t;
            }
        }

        /* Pass 2: each block replays the original body from its carry-in. */
#pragma omp parallel for schedule(static) shared(a, b, bs, nb)
        for (int j = 0; j < nb; j++) {
            long lo = ((long)LEN_1D * j) / nb;
            long hi = ((long)LEN_1D * (j + 1)) / nb;
            real_t s = bs[j];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }

        /* The original's final sum is the last value written to b. */
        if (LEN_1D > 0) {
            sum = b[LEN_1D - 1];
        }

        pb_mix(nl);
    }
    return sum;
}

PB_MAIN(kernel_s3112)
