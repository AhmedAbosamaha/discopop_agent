#include "data.h"

real_t kernel_s293(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* a[0] is only rewritten with its own value (i == 0), so every
           iteration reads the same value: hoist it before the loop. */
        real_t a0 = a[0];
        #pragma omp parallel for default(none) shared(a) firstprivate(a0) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a0;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
