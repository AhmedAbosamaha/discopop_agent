#include "data.h"

real_t kernel_s112(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b)
        for (int i = LEN_1D - 2; i >= 0; i--) {
            a[i+1] = a[i] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
