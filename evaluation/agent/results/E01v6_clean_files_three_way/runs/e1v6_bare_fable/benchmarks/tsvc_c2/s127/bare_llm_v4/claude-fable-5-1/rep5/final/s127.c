#include "data.h"

real_t kernel_s127(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        /* j is an induction variable: j = 2*i (first store) and 2*i+1
           (second store).  Compute it per iteration so there is no
           loop-carried dependence. */
#pragma omp parallel for default(none) shared(a, b, c, d, e) schedule(static)
        for (int i = 0; i < LEN_1D/2; i++) {
            int j0 = 2 * i;
            a[j0] = b[i] + c[i] * d[i];
            a[j0 + 1] = b[i] + d[i] * e[i];
        }
        j = 2 * (LEN_1D/2) - 1;
        dummy(a, b, c, d, e);
    }
    (void)j;
    return (real_t)0;
}
