#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Path 1: Execute a[i] = c[i] + d[i] * e[i] for all i where b[i] >= 0
        // Each iteration i writes to a[i] and reads from c[i], d[i], e[i]
        // No loop-carried dependence: different iterations access different indices
        #pragma omp parallel for schedule(static) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }

        // Path 2: Execute c[i+1] = a[i] + d[i] * d[i] for all i where b[i] < 0
        // Each iteration i reads from a[i] and writes to c[i+1]
        // No loop-carried dependence: iteration i writes c[i+1], iteration i+1 writes c[i+2]
        // Different indices prevent racing
        #pragma omp parallel for schedule(static) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
