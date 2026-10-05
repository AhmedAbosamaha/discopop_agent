#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* a[i] = (b[i] + b[i-1] + b[i-2]) * .333, with b indexed modulo
         * LEN_1D so that i==0 uses b[LEN_1D-1] and b[LEN_1D-2], and i==1
         * uses b[0] and b[LEN_1D-1] -- matching the original recurrence
         * that carried x=b[i-1], y=b[i-2] forward through the loop.
         * Expressing the lag via indexing removes the loop-carried
         * dependence on x/y, so iterations of i become independent. */
        #pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i == 0) ? LEN_1D - 1 : i - 1;
            int im2 = (i <= 1) ? LEN_1D - 2 + i : i - 2;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
