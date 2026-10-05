#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for default(none) shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            real_t prev = (i == 0) ? b[LEN_1D-1] : b[i-1];
            a[i] = (b[i] + prev) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
