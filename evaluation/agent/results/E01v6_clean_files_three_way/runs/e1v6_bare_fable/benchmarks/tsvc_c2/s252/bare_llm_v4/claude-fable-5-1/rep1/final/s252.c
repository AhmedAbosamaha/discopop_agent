#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original: t = 0; for i: s = b[i]*c[i]; a[i] = s + t; t = s;
         * so a[i] = b[i]*c[i] + b[i-1]*c[i-1] for i >= 1, and a[0] = b[0]*c[0].
         * The carried scalar t is recomputed from b/c, removing the dependence. */
        a[0] = b[0] * c[0] + (real_t) 0.;
#pragma omp parallel for default(none) shared(a, b, c) schedule(static)
        for (int i = 1; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t t = b[i - 1] * c[i - 1];
            a[i] = s + t;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
