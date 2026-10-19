#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t prev_prod = (i == 0) ? 0.0 : b[i-1] * c[i-1];
            a[i] = s + prev_prod;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
