#include "data.h"

real_t kernel_s291(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* im1 is not a carried value: at index i it is always i-1 (wrapping
         * to LEN_1D-1 at i==0). Compute it locally per iteration so each
         * iteration only reads b[] and writes its own a[i], removing the
         * loop-carried dependence and allowing the loop to run in any order. */
        #pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? LEN_1D - 1 : i - 1;
            a[i] = (b[i] + b[im1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
