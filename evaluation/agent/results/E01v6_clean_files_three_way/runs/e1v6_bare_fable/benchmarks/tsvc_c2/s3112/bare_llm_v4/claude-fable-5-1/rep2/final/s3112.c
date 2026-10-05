#include "data.h"

/* Number of blocks for the two-pass scan.  Fixed (not tied to the thread
 * count) so that every thread count and schedule computes the same values. */
#define S3112_NB 128

real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    real_t bsum[S3112_NB];
    real_t boff[S3112_NB];

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: per-block partial sums of a[]. */
        #pragma omp parallel for schedule(static) shared(a, bsum)
        for (int k = 0; k < S3112_NB; k++) {
            int lo = (int)(((long)LEN_1D * k) / S3112_NB);
            int hi = (int)(((long)LEN_1D * (k + 1)) / S3112_NB);
            real_t s = (real_t)0.0;
            for (int i = lo; i < hi; i++) {
                s += a[i];
            }
            bsum[k] = s;
        }

        /* Exclusive scan of the block sums: starting offset of each block. */
        {
            real_t run = (real_t)0.0;
            for (int k = 0; k < S3112_NB; k++) {
                boff[k] = run;
                run += bsum[k];
            }
        }

        /* Pass 2: each block writes its own disjoint slice of b[]. */
        #pragma omp parallel for schedule(static) shared(a, b, boff)
        for (int k = 0; k < S3112_NB; k++) {
            int lo = (int)(((long)LEN_1D * k) / S3112_NB);
            int hi = (int)(((long)LEN_1D * (k + 1)) / S3112_NB);
            real_t s = boff[k];
            for (int i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }

        /* The original's final `sum` equals b[LEN_1D-1] before dummy(). */
        sum = b[LEN_1D - 1];

        dummy(a, b, c, d, e);
    }
    return sum;
}
