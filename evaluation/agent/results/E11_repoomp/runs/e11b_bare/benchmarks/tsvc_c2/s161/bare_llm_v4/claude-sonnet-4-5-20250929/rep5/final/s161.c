#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Update a[i] where b[i] >= 0
        // All reads of c[] happen here before phase 2 writes to c[]
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }

        // Phase 2: Update c[i+1] where b[i] < 0
        // All writes to a[] from phase 1 complete before reads here
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
