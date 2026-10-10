#include "data.h"

real_t kernel_s127(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i+1] = b[i] + d[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
