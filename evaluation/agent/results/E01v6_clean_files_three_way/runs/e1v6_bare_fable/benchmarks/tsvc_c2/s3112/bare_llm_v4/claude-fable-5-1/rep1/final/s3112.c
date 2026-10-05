#include "data.h"

#define NCHUNK 128

real_t kernel_s3112(void)
{
    real_t sum = (real_t)0.0;
    real_t partial[NCHUNK];
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: per-chunk totals (reads a only) */
#pragma omp parallel for shared(a, partial)
        for (int c = 0; c < NCHUNK; c++) {
            long lo = (long)LEN_1D * c / NCHUNK;
            long hi = (long)LEN_1D * (c + 1) / NCHUNK;
            real_t s = (real_t)0.0;
            for (long i = lo; i < hi; i++) {
                s += a[i];
            }
            partial[c] = s;
        }
        /* serial exclusive scan over the chunk totals -> chunk offsets */
        real_t run = (real_t)0.0;
        for (int c = 0; c < NCHUNK; c++) {
            real_t t = partial[c];
            partial[c] = run;
            run += t;
        }
        sum = run;
        /* pass 2: sequential scan inside each chunk from its offset */
#pragma omp parallel for shared(a, b, partial)
        for (int c = 0; c < NCHUNK; c++) {
            long lo = (long)LEN_1D * c / NCHUNK;
            long hi = (long)LEN_1D * (c + 1) / NCHUNK;
            real_t s = partial[c];
            for (long i = lo; i < hi; i++) {
                s += a[i];
                b[i] = s;
            }
        }
        dummy(a, b, c, d, e);
    }
    return sum;
}
