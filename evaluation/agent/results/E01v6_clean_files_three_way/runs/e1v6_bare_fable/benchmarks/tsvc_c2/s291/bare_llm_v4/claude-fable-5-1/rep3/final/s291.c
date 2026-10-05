#include "data.h"

real_t kernel_s291(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* im1 was a running "previous index": i-1, wrapping to LEN_1D-1 at i == 0.
           Computing it directly from i removes the loop-carried scalar dependence. */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? (LEN_1D - 1) : (i - 1);
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
