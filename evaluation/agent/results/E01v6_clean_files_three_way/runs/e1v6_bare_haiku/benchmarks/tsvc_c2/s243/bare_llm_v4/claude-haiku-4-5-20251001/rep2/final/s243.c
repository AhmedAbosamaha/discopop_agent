#include "data.h"
#include <string.h>

real_t kernel_s243(void)
{
    real_t *a_init = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Save initial values of a before modifying */
        memcpy(a_init, a, LEN_1D * sizeof(real_t));

        /* Pass 1: Compute a[i] and b[i] in parallel.
           Each iteration i writes only to a[i] and b[i], no loop-carried dependencies. */
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
        }

        /* Pass 2: Compute final a[i] values in parallel using saved initial values.
           Each iteration i reads a_init[i+1] (initial values, not modified by Pass 1)
           and writes only to a[i]. No loop-carried dependencies. */
        #pragma omp parallel for shared(a, b, d, a_init)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + a_init[i+1] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_init);
    return (real_t)0;
}
