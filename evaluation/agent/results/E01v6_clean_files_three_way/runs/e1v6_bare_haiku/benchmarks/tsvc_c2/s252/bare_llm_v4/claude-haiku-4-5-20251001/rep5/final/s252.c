#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static) shared(a, b, c)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b[i] * c[i] + (i > 0 ? b[i-1] * c[i-1] : (real_t)0.0);
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
