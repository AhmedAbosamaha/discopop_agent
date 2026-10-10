#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: the b[i] < 0 branch.  Each iteration writes its own
           c[i+1] and reads only a[i] (which this branch never writes)
           and d[i], so iterations are independent. */
#pragma omp parallel for default(none) shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        /* Pass 2: the b[i] >= 0 branch.  All c writes from pass 1 are
           complete, so c[i] holds the value the original sequential
           order would have seen.  Each iteration writes its own a[i]. */
#pragma omp parallel for default(none) shared(a, b, c, d, e) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (!(b[i] < (real_t)0.)) {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
