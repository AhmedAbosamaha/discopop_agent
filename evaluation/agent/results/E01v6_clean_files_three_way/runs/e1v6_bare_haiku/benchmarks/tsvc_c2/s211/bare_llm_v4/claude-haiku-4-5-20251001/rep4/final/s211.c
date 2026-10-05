#include "data.h"
#include <stdlib.h>

real_t kernel_s211(void)
{
    // Allocate temporary buffer for new b values to break loop-carried dependence
    real_t *b_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Parallelize inner loop: each iteration reads from original b and c,d,e
        // and writes to independent elements of a and b_new (no inter-iteration dependence)
        #pragma omp parallel for shared(a, b, c, d, e, b_new)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
            b_new[i] = b[i + 1] - e[i] * d[i];
        }

        // Copy b_new back to b (sequential): dependence is moved here
        // All parallel reads complete before any writes to b occur
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_new[i];
        }

        dummy(a, b, c, d, e);
    }

    free(b_new);
    return (real_t)0;
}
