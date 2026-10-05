#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* x at iteration i is always b[i-1] (wrapping to b[LEN_1D-1] at i==0).
         * Reconstructing it from b directly removes the loop-carried
         * dependence through x, so iterations become independent. */
        #pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            real_t x = (i == 0) ? b[LEN_1D-1] : b[i-1];
            a[i] = (b[i] + x) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
