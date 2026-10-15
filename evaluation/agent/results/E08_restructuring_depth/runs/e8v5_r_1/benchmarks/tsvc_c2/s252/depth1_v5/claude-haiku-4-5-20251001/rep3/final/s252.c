#include "data.h"

real_t kernel_s252(void)
{
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        a[i] = b[i] * c[i] + (i > 0 ? b[i-1] * c[i-1] : (real_t)0.);
    }
    for (int nl = 1; nl < iterations; nl++) {
        dummy(a, b, c, d, e);
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b[i] * c[i] + (i > 0 ? b[i-1] * c[i-1] : (real_t)0.);
        }
    }
    dummy(a, b, c, d, e);
    return (real_t)0;
}
