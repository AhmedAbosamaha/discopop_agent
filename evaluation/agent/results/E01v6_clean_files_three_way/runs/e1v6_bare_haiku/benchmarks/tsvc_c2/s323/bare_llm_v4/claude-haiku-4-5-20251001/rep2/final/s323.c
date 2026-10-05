#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute a[i] from b[i-1]. Each iteration reads a different
        // element of b (b[i-1]), so all iterations are independent.
        #pragma omp parallel for shared(a, b, c, d)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }

        // Phase 2: Compute b[i] from a[i]. Each iteration reads a different
        // element of a (a[i]), so all iterations are independent.
        #pragma omp parallel for shared(a, b, c, e)
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = a[i] + c[i] * e[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
