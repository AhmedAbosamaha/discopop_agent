#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /*
         * Original recurrence: t starts at 0, and for each i,
         *   s = b[i]*c[i]; a[i] = s + t; t = s;
         * so t going into iteration i equals s computed at iteration i-1,
         * i.e. t(i) = b[i-1]*c[i-1] for i>0, and t(0) = 0.
         * This lets a[i] be computed directly from b[] and c[] without
         * carrying any value from the previous iteration, removing the
         * loop-carried dependence entirely.
         */
        #pragma omp parallel for default(none) shared(a, b, c)
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t t = (i > 0) ? (b[i - 1] * c[i - 1]) : (real_t) 0.;
            a[i] = s + t;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
