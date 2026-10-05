#include "data.h"

real_t kernel_s000(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b[i] + 1;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
