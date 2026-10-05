#include "data.h"

real_t kernel_s291(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* im1 was carried as (i-1) with wraparound to LEN_1D-1 at i==0.
         * It only ever selects an index into b[], never a value produced
         * by a previous iteration of this loop, so each iteration can
         * recompute it independently from i. a[i] is written exactly
         * once per i (disjoint locations) and b is only read, so the
         * iterations are now fully independent. */
        #pragma omp parallel for schedule(static) default(none) shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? LEN_1D - 1 : i - 1;
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
