#include "data.h"

real_t kernel_s211(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Parallel loop 1: compute a[i] from b[i-1]
        // No loop-carried dependence: each iteration writes to a[i] and reads distinct b values
        #pragma omp parallel for shared(a, b, c, d) private(i)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }

        // Parallel loop 2: compute b[i] from b[i+1]
        // No loop-carried dependence: iteration i writes b[i], iteration i+1 reads b[i+2]
        #pragma omp parallel for shared(b, e, d) private(i)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b[i + 1] - e[i] * d[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
