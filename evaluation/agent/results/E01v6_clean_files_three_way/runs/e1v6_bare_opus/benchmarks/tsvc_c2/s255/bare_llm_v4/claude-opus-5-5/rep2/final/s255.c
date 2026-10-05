#include "data.h"

real_t kernel_s255(void)
{
    real_t x, y;
    for (int nl = 0; nl < iterations; nl++) {
        x = b[LEN_1D-1];
        y = b[LEN_1D-2];
        /* x and y are just b[i-1] and b[i-2] (wrapping for i = 0, 1) */
        a[0] = (b[0] + x + y) * (real_t).333;
        a[1] = (b[1] + b[0] + x) * (real_t).333;
        #pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1] + b[i-2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
