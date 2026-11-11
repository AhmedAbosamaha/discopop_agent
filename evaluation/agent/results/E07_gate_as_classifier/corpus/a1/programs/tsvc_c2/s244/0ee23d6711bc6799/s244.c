#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t a_last = a[LEN_1D-1];
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + a_last * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
