#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = (b[i-1] + c[i] * d[i]) + c[i] * e[i];
        }
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
