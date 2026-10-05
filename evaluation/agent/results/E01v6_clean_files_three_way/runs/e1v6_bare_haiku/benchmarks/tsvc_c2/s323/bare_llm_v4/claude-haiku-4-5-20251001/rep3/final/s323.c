#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = a[i] + c[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
