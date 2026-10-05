#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* b[i] needs the OLD a[i+1] (overwritten only by a later iteration),
           so compute all of b first from the untouched a. */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, d)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }
        /* a[i] needs the NEW b[i-1] (b[0] is never written). */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
