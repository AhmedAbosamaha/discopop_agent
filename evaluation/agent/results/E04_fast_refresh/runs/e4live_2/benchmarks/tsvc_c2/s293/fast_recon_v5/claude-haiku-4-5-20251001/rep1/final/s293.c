#include "data.h"

real_t kernel_s293(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t a0_val = a[0];
        #pragma omp parallel for firstprivate(a0_val) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a0_val;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
