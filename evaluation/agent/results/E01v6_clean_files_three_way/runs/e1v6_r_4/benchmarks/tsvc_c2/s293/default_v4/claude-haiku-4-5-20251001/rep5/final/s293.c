#include "data.h"

real_t kernel_s293(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        a[0] = a[0];
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = a[0];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
