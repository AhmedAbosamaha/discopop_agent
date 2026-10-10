#include "data.h"
#include <stdlib.h>

real_t kernel_s211(void)
{
    real_t *b_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Phase 1: compute new b values in parallel, reading from original b */
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b_new[i] = b[i + 1] - e[i] * d[i];
        }

        /* Copy computed values back to b */
        #pragma omp parallel for shared(b_new) 
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_new[i];
        }

        /* Phase 2: compute a values in parallel, reading updated b */
        #pragma omp parallel for schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(b_new);
    return (real_t)0;
}
