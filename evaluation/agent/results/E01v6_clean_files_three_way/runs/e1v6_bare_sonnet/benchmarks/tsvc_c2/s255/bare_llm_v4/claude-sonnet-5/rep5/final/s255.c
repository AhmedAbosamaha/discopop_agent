#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original recurrence: x holds b[i-1], y holds b[i-2] (wrapping
         * around to the end of b for i==0 and i==1). Both are pure
         * functions of i and the read-only array b, so the dependence
         * is eliminated by computing the wrapped indices directly. */
#pragma omp parallel for shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i - 1 + LEN_1D) % LEN_1D;
            int im2 = (i - 2 + LEN_1D) % LEN_1D;
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
