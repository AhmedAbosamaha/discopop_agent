#include "data.h"

real_t kernel_s293(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t temp = a[0];
        #pragma omp parallel for shared(a)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = temp;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
