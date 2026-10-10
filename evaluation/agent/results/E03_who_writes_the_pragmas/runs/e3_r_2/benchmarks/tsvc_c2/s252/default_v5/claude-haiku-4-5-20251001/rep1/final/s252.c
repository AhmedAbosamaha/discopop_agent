#include "data.h"

real_t kernel_s252(void)
{
    real_t s;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(s) 
        for (int i = 0; i < LEN_1D; i++) {
            s = b[i] * c[i];
            a[i] = s + (i > 0 ? b[i-1] * c[i-1] : 0.0);
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
