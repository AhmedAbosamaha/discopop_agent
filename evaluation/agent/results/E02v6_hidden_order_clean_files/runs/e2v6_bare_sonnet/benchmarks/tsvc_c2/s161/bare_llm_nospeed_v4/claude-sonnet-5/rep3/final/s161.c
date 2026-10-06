#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for default(none) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                /* Writes c[i+1]; reads a[i], d[i] which are never written
                   during this loop pass for index i (that would require
                   taking the else branch below for the same i). */
                c[i+1] = a[i] + d[i] * d[i];
            } else {
                /* Need the value c[i] would have had at this point in the
                   original sequential execution. Only iteration i-1 could
                   have modified c[i] (by taking the branch above), and it
                   does so using only the original a[i-1], d[i-1] (which
                   iteration i-1 never writes in that case). Recompute that
                   value directly instead of reading c[i], which removes
                   the cross-iteration race while keeping the same result. */
                real_t cval;
                if (i == 0) {
                    cval = c[0];
                } else if (b[i-1] < (real_t)0.) {
                    cval = a[i-1] + d[i-1] * d[i-1];
                } else {
                    cval = c[i];
                }
                a[i] = cval + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
