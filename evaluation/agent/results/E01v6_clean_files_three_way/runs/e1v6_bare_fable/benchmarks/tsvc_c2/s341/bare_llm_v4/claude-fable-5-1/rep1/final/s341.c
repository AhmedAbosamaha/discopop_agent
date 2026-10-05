#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    /* Number of chunks used for the two-pass stream compaction.  Fixed, so
       the per-chunk bookkeeping does not grow with the input. */
    const int nch = (LEN_1D < 1024) ? LEN_1D : 1024;
    long *cnt = (long *)malloc((size_t)(nch + 1) * sizeof(long));
    int ch;

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: count positives in each chunk. */
        #pragma omp parallel for schedule(static) shared(cnt, b) firstprivate(nch)
        for (ch = 0; ch < nch; ch++) {
            long lo = ((long)LEN_1D * ch) / nch;
            long hi = ((long)LEN_1D * (ch + 1)) / nch;
            long c_local = 0;
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    c_local++;
                }
            }
            cnt[ch] = c_local;
        }

        /* Serial exclusive prefix sum: cnt[ch] becomes the output offset
           of chunk ch in a[]. */
        {
            long run = 0;
            for (ch = 0; ch < nch; ch++) {
                long t = cnt[ch];
                cnt[ch] = run;
                run += t;
            }
            cnt[nch] = run;
        }

        /* Pass 2: each chunk writes its positives to its own disjoint
           output range, preserving the original order. */
        #pragma omp parallel for schedule(static) shared(cnt, a, b) firstprivate(nch)
        for (ch = 0; ch < nch; ch++) {
            long lo = ((long)LEN_1D * ch) / nch;
            long hi = ((long)LEN_1D * (ch + 1)) / nch;
            long j = cnt[ch];
            for (long i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[j] = b[i];
                    j++;
                }
            }
        }

        dummy(a, b, c, d, e);
    }

    free(cnt);
    return (real_t)0;
}
