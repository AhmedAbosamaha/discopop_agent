#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: all c[i+1] updates (the values iteration i+1 of the
         * original would read).  Writes distinct c[i+1]; reads only a, d. */
#pragma omp parallel for default(none) shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        /* Pass 2: all a[i] updates, reading the c produced by pass 1.
         * Writes distinct a[i]; reads only b, c, d, e. */
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
