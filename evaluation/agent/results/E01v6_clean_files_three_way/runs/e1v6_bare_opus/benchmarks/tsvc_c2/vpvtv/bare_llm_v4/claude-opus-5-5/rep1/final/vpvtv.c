#include "data.h"

real_t kernel_vpvtv(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for default(none) shared(a, b, c) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] += b[i] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
