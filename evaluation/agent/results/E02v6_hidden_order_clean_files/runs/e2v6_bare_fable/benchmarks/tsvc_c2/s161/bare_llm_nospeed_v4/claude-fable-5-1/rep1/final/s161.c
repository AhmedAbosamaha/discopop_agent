#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: the branch that writes c[i+1].  It reads a[i], which no
         * other iteration (and not this one, in this branch) modifies, so
         * all these writes are independent of each other. */
#pragma omp parallel for default(none) shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        /* Pass 2: the branch that reads c[i] (possibly produced by
         * iteration i-1 in pass 1, which has fully completed) and writes
         * a[i]; each iteration touches only its own a[i]. */
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
