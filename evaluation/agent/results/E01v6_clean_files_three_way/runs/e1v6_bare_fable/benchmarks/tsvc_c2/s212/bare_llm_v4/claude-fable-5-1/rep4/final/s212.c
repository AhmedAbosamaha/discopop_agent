#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: every b[i] reads the ORIGINAL a[i+1] (anti-dependence removed by
         * finishing all reads of a before any write to a). */
#pragma omp parallel for default(none) shared(a, b, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }
        /* Pass 2: scale a; independent per element. */
#pragma omp parallel for default(none) shared(a, c) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
