#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: b uses the old (not yet scaled) a[i+1] */
        #pragma omp parallel for default(none) shared(a, b, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }
        /* pass 2: scale a after all reads of the old values are done */
        #pragma omp parallel for default(none) shared(a, c) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
