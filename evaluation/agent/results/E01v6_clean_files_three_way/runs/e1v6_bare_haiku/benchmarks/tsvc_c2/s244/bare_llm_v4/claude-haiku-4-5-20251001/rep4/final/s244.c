#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Parallelizable loop: each iteration writes to unique a[i] and b[i]
        #pragma omp parallel for schedule(static) \
            private(i) shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }

        // Compute final element a[LEN_1D-1] separately
        // (uses the last b value computed above)
        a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
