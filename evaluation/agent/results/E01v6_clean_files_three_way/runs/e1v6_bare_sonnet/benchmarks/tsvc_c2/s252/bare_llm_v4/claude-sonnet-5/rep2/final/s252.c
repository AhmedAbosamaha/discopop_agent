#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b, c)
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t tprev = (i == 0) ? (real_t) 0. : b[i - 1] * c[i - 1];
            a[i] = s + tprev;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
