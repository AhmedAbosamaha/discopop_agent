#include "data.h"

real_t kernel_s291(void)
{
    int im1;
    for (int nl = 0; nl < iterations; nl++) {
        /* im1 is just i-1 (wrapping to LEN_1D-1 at i==0): peel i==0 and
           compute the index directly so iterations are independent. */
        im1 = LEN_1D-1;
        a[0] = (b[0] + b[im1]) * (real_t).5;
        #pragma omp parallel for schedule(static) default(none) shared(a, b)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        im1 = LEN_1D-1;
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
