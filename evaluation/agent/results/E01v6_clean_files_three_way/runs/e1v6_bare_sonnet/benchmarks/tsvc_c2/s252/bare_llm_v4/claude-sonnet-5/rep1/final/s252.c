#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original recurrence: t_i = s_{i-1} = b[i-1]*c[i-1], t_0 = 0.
         * Recompute that value directly from b/c instead of carrying it
         * through t, which removes the loop-carried dependence and makes
         * each iteration independent. */
        #pragma omp parallel for shared(a, b, c)
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = b[i] * c[i];
            real_t t_prev = (i == 0) ? (real_t) 0. : b[i - 1] * c[i - 1];
            a[i] = s + t_prev;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
