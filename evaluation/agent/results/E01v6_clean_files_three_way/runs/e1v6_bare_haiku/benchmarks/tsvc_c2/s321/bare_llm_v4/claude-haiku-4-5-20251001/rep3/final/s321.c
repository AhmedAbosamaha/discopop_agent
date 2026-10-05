#include "data.h"

real_t kernel_s321(void)
{
    #pragma omp parallel for shared(a, b, c, d, e)
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += a[i-1] * b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
