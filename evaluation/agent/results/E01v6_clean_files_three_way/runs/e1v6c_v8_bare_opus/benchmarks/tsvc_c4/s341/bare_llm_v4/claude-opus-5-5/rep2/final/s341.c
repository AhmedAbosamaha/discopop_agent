#include "data.h"

#define S341_NB 256

real_t kernel_s341(void)
{
    int cnt[S341_NB];
    int off[S341_NB];
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: count positives per block */
        #pragma omp parallel for default(none) shared(b, cnt) schedule(static)
        for (int k = 0; k < S341_NB; k++) {
            int lo = (int)((long long)k * LEN_1D / S341_NB);
            int hi = (int)((long long)(k + 1) * LEN_1D / S341_NB);
            int c0 = 0;
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    c0++;
                }
            }
            cnt[k] = c0;
        }

        /* pass 2: exclusive prefix sum (initial j = -1, first write at 0) */
        int run = 0;
        for (int k = 0; k < S341_NB; k++) {
            off[k] = run;
            run += cnt[k];
        }

        /* pass 3: scatter each block into its disjoint range of a */
        #pragma omp parallel for default(none) shared(a, b, off) schedule(static)
        for (int k = 0; k < S341_NB; k++) {
            int lo = (int)((long long)k * LEN_1D / S341_NB);
            int hi = (int)((long long)(k + 1) * LEN_1D / S341_NB);
            int jj = off[k];
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[jj] = b[i];
                    jj++;
                }
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
