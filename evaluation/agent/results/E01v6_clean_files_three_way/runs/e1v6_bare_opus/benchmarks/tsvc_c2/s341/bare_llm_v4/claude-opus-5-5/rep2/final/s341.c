#include "data.h"

#define NCHUNK 256

real_t kernel_s341(void)
{
    long cnt[NCHUNK];
    long off[NCHUNK];
    for (int nl = 0; nl < iterations; nl++) {
        int k;
#pragma omp parallel for default(none) shared(b, cnt) schedule(static)
        for (k = 0; k < NCHUNK; k++) {
            long lo = (long)k * LEN_1D / NCHUNK;
            long hi = (long)(k + 1) * LEN_1D / NCHUNK;
            long c0 = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    c0++;
                }
            }
            cnt[k] = c0;
        }

        long run = 0;
        for (k = 0; k < NCHUNK; k++) {
            off[k] = run;
            run += cnt[k];
        }

#pragma omp parallel for default(none) shared(a, b, off) schedule(static)
        for (k = 0; k < NCHUNK; k++) {
            long lo = (long)k * LEN_1D / NCHUNK;
            long hi = (long)(k + 1) * LEN_1D / NCHUNK;
            long j = off[k];
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[j] = b[i];
                    j++;
                }
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
