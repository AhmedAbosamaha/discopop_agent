#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* i = 0 and i = 1 read the wrapped-around elements b[LEN_1D-1], b[LEN_1D-2] */
        a[0] = (b[0] + b[LEN_1D-1] + b[LEN_1D-2]) * (real_t).333;
        a[1] = (b[1] + b[0] + b[LEN_1D-1]) * (real_t).333;
        /* for i >= 2 the carried x,y are exactly b[i-1], b[i-2] */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1] + b[i-2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
