#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: handle cases where b[i] < 0
        #pragma omp parallel for shared(b, a, d, c)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }

        // Second pass: handle cases where b[i] >= 0
        #pragma omp parallel for shared(b, c, d, e, a)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
