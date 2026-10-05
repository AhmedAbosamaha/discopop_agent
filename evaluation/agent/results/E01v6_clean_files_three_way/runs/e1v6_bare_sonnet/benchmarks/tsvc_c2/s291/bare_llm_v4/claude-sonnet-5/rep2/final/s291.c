#include "data.h"

real_t kernel_s291(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original recurrence: im1 starts at LEN_1D-1, then becomes i-1
         * each iteration (i.e. im1 = (i==0) ? LEN_1D-1 : i-1).  That value
         * is a function of i alone, not of work done in a prior iteration,
         * so each iteration can compute its own "previous index" directly
         * and the iterations become independent. */
        #pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? LEN_1D - 1 : i - 1;
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
