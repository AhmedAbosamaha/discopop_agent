#include "data.h"

real_t kernel_s293(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t a_0 = a[0];
        #pragma omp parallel for firstprivate(a_0) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a_0;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
