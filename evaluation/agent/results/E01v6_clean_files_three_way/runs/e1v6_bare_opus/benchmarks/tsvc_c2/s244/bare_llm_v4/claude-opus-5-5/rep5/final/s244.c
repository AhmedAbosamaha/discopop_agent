#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        /* only the last iteration's write of a[i+1] survives; earlier ones
           are overwritten by the next iteration's first statement */
        a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
