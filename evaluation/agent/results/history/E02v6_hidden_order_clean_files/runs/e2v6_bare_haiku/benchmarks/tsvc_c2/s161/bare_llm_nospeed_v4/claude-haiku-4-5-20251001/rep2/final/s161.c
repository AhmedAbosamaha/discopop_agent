#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: handle b[i] >= 0 cases
        // Each iteration i independently reads c[i], d[i], e[i], b[i] and writes a[i]
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }

        // Second pass: handle b[i] < 0 cases
        // Each iteration i independently reads a[i], d[i], b[i] and writes c[i+1]
        // No loop-carried dependence on c within this pass
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
