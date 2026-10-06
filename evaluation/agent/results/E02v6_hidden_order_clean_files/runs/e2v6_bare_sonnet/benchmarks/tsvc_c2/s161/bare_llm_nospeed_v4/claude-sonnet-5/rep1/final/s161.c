#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Each iteration i writes either a[i] or c[i+1], never both, and
         * never an index any other iteration writes.  The only read that
         * could otherwise observe another iteration's write is c[i] in
         * the else-branch, which equals what iteration i-1 would have
         * stored there (a[i-1] + d[i-1]*d[i-1]) when b[i-1] < 0 -- so we
         * recompute that value from the untouched old a/d instead of
         * reading the (possibly not-yet-written, order-dependent) c[i]
         * slot.  That removes the cross-iteration dependence entirely. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            } else {
                real_t c_i;
                if (i > 0 && b[i-1] < (real_t)0.) {
                    c_i = a[i-1] + d[i-1] * d[i-1];
                } else {
                    c_i = c[i];
                }
                a[i] = c_i + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
