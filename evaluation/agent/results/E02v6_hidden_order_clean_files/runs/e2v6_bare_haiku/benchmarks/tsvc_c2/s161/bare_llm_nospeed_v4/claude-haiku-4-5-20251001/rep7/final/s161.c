#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Process even iterations in parallel: 0, 2, 4, ...
        // These write to disjoint array elements, so they're independent
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; i += 2) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            } else {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        // Implicit synchronization barrier at end of parallel for

        // Process odd iterations in parallel: 1, 3, 5, ...
        // These write to disjoint array elements, so they're independent
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 1; i < LEN_1D-1; i += 2) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            } else {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
