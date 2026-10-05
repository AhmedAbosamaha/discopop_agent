#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* First parallel loop: compute a[i] *= c[i] for all i */
        #pragma omp parallel for shared(a, c) default(none)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }

        /* Second parallel loop: compute b[i] += a[i+1] * d[i] for all i */
        #pragma omp parallel for shared(a, b, d) default(none)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
