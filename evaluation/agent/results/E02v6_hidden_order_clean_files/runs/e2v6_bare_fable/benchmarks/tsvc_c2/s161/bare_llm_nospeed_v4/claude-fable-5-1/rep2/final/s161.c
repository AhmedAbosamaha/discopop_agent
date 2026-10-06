#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: all writes to c[i+1].  Each iteration writes a distinct
         * c[i+1] and reads a[i], d[i], which no iteration of this pass
         * modifies, so the iterations are independent. */
#pragma omp parallel for default(none) shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        /* Pass 2: all writes to a[i].  c is now final (pass 1 completed),
         * each iteration writes a distinct a[i]. */
#pragma omp parallel for default(none) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (!(b[i] < (real_t)0.)) {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
