#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s241(void)
{
    /* old_a holds a snapshot of a[] taken before each sweep overwrites it,
     * so that the read of a[i+1] inside the loop always sees the same
     * pre-sweep value it would have seen in the original sequential
     * execution order (where iteration i+1 hasn't run yet when b[i] is
     * computed). This breaks the loop-carried dependence between
     * iterations i and i+1 and makes every iteration independent. */
    real_t *old_a = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(old_a, a, sizeof(real_t) * (size_t)LEN_1D);

        /* Each iteration i only touches a[i] and b[i] for writes, and
         * reads b[i], c[i], d[i] (its own index, before being
         * overwritten) plus old_a[i+1] (a read-only snapshot fixed
         * before this loop starts). No cross-iteration data hazard
         * remains, so the iterations can run in any order/schedule. */
        #pragma omp parallel for default(none) shared(a, b, c, d, old_a) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * old_a[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(old_a);
    return (real_t)0;
}
