#include "data.h"

#define S341_NCHUNK 256

real_t kernel_s341(void)
{
    int j;
    long cnt[S341_NCHUNK];
    long off[S341_NCHUNK];

    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: count positives in each contiguous chunk of b */
#pragma omp parallel for schedule(static) default(none) shared(b, cnt)
        for (int ch = 0; ch < S341_NCHUNK; ch++) {
            long lo = (long)ch * LEN_1D / S341_NCHUNK;
            long hi = (long)(ch + 1) * LEN_1D / S341_NCHUNK;
            long n = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    n++;
                }
            }
            cnt[ch] = n;
        }

        /* serial exclusive scan over chunk counts */
        long total = 0;
        for (int ch = 0; ch < S341_NCHUNK; ch++) {
            off[ch] = total;
            total += cnt[ch];
        }
        j = (int)total - 1;

        /* pass 2: each chunk packs its positives at its own offset */
#pragma omp parallel for schedule(static) default(none) shared(a, b, off)
        for (int ch = 0; ch < S341_NCHUNK; ch++) {
            long lo = (long)ch * LEN_1D / S341_NCHUNK;
            long hi = (long)(ch + 1) * LEN_1D / S341_NCHUNK;
            long k = off[ch];
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[k] = b[i];
                    k++;
                }
            }
        }

        (void)j;
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
