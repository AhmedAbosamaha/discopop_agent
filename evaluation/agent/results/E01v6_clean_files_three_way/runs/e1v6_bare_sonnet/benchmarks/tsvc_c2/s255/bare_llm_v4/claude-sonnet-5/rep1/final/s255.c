#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original recurrence: x = b[i-1], y = b[i-2] (wrapping around at
         * the start of the array using b[LEN_1D-1] and b[LEN_1D-2]).
         * That just reuses prior b[] values, so we can index directly
         * instead of carrying x/y forward between iterations, which makes
         * every iteration of i independent. */
        #pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? LEN_1D - 1 : i - 1;
            int im2 = (i == 0) ? LEN_1D - 2 : ((i == 1) ? LEN_1D - 1 : i - 2);
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
