#include "data.h"

/* Number of chunks for the two-pass pack.  Fixed (independent of the
 * thread count) so that every thread count / schedule produces the exact
 * same assignment of elements to positions in a[]. */
#define S341_NCHUNK 512

real_t kernel_s341(void)
{
    int j;
    const int chunk = (LEN_1D + S341_NCHUNK - 1) / S341_NCHUNK;
    int counts[S341_NCHUNK];   /* constant size: does not grow with input */

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: count positives in each chunk (independent chunks). */
        #pragma omp parallel for schedule(static) shared(b, counts, chunk)
        for (int cidx = 0; cidx < S341_NCHUNK; cidx++) {
            int lo = cidx * chunk;
            int hi = lo + chunk;
            if (hi > LEN_1D) hi = LEN_1D;
            int cnt = 0;
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    cnt++;
                }
            }
            counts[cidx] = cnt;
        }

        /* Serial exclusive scan over the (constant number of) chunk counts:
         * counts[cidx] becomes the index in a[] where chunk cidx starts. */
        int total = 0;
        for (int cidx = 0; cidx < S341_NCHUNK; cidx++) {
            int c0 = counts[cidx];
            counts[cidx] = total;
            total += c0;
        }

        /* Pass 2: each chunk packs its positives into its own disjoint
         * range of a[], starting at its precomputed offset. */
        #pragma omp parallel for schedule(static) shared(a, b, counts, chunk)
        for (int cidx = 0; cidx < S341_NCHUNK; cidx++) {
            int lo = cidx * chunk;
            int hi = lo + chunk;
            if (hi > LEN_1D) hi = LEN_1D;
            int jj = counts[cidx];
            for (int i = lo; i < hi; i++) {
                if (b[i] > (real_t)0.) {
                    a[jj] = b[i];
                    jj++;
                }
            }
        }

        j = total - 1;   /* same final value the sequential counter reached */
        (void)j;
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
