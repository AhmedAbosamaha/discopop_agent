#include "data.h"

real_t kernel_s255(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* i = 0: x = b[N-1], y = b[N-2];  i = 1: x = b[0], y = b[N-1] */
        a[0] = (b[0] + b[LEN_1D-1] + b[LEN_1D-2]) * (real_t).333;
        a[1] = (b[1] + b[0] + b[LEN_1D-1]) * (real_t).333;
        /* i >= 2: x = b[i-1], y = b[i-2] */
        #pragma omp parallel for schedule(static) default(none) shared(a, b)
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1] + b[i-2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
