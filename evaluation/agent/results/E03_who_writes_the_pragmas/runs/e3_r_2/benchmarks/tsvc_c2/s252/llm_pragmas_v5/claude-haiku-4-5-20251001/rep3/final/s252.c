#include "data.h"

real_t kernel_s252(void)
{
    real_t t, s;
    for (int nl = 0; nl < iterations; nl++) {
        // First iteration: a[0] = b[0]*c[0] + 0
        s = b[0] * c[0];
        a[0] = s;

        // Remaining iterations: a[i] = b[i]*c[i] + b[i-1]*c[i-1]
        #pragma omp parallel for schedule(static) private(s)
        for (int i = 1; i < LEN_1D; i++) {
            s = b[i] * c[i];
            a[i] = s + b[i-1] * c[i-1];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
