#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* i == 0 uses the wrapped-around predecessor b[LEN_1D-1]. */
        a[0] = (b[0] + b[LEN_1D-1]) * (real_t).5;
        /* For i >= 1 the carried scalar x equals b[i-1]; b is read-only here,
           so every iteration is independent. */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
