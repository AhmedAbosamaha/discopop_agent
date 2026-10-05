#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Phase 1: compute a[i] values in parallel
           Each iteration i reads b[i-1], c[i], d[i] and writes a[i].
           No iteration depends on a[j] writes from other iterations,
           and b is read-only in this phase. */
        #pragma omp parallel for shared(a, b, c, d)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }

        /* Phase 2: compute b[i] values in parallel
           Each iteration i reads a[i] (computed in phase 1), c[i], e[i]
           and writes b[i]. No iteration depends on b[j] writes from other
           iterations, and a is read-only in this phase. */
        #pragma omp parallel for shared(a, b, c, e)
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = a[i] + c[i] * e[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
