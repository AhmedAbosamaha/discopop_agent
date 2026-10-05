#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    /* nb[i] holds the new b[i] (i = 1..LEN_1D-2); nb[0] holds b[0],
       which the original never writes and a[1] reads. */
    real_t *nb = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        nb[0] = b[0];
        /* Phase 1: new b from the OLD b[i+1] (no in-place overwrite). */
        #pragma omp parallel for default(none) shared(nb, b, d, e) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            nb[i] = b[i + 1] - e[i] * d[i];
        }
        /* Phase 2: a[i] uses the NEW b[i-1]; commit new b. */
        #pragma omp parallel for default(none) shared(nb, a, b, c, d) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = nb[i - 1] + c[i] * d[i];
            b[i] = nb[i];
        }
        dummy(a, b, c, d, e);
    }
    free(nb);
    return (real_t)0;
}
