#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* x at the start of iteration i is just b[i-1] (wrapping to
         * b[LEN_1D-1] for i==0).  Reading b[i-1] directly removes the
         * carried dependence, so each iteration becomes independent. */
        a[0] = (b[0] + b[LEN_1D-1]) * (real_t).5;
#pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
