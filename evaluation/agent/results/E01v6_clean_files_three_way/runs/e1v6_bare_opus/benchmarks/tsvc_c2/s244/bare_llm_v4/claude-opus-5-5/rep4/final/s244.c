#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* a[i+1] written by iteration i is always overwritten by iteration
           i+1 (which does not read it first), except for the last one.
           So only the final a[LEN_1D-1] store survives; peel it out. */
        #pragma omp parallel for schedule(static) shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        {
            int i = LEN_1D-2;
            a[i+1] = b[i] + a[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
