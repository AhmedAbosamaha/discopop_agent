#include "data.h"

real_t kernel_s293(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t a0_cached = a[0];
        #pragma omp parallel for firstprivate(a0_cached) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a0_cached;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
