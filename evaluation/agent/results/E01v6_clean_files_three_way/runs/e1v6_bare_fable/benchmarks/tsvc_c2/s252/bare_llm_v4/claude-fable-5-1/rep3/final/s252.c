#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* i == 0: previous product t is 0 */
        a[0] = b[0] * c[0] + (real_t) 0.;
        /* The carried scalar t equals b[i-1]*c[i-1]; recompute it so
           every iteration is independent.  b and c are read-only here. */
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
