#include "data.h"
#include <stdlib.h>

real_t kernel_s323(void)
{
    /* Scratch buffer holding c[i]*(d[i]+e[i]); reused across outer
     * iterations, heap-allocated since LEN_1D can be very large. */
    real_t *s = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: s[i] depends only on c[i], d[i], e[i] -- independent
         * across i, so this can run in parallel. */
        #pragma omp parallel for default(none) shared(c, d, e, s)
        for (int i = 1; i < LEN_1D; i++) {
            s[i] = c[i] * (d[i] + e[i]);
        }

        /* Pass 2: true recurrence b[i] = b[i-1] + s[i]
         * (since original b[i] = a[i] + c[i]*e[i]
         *              = b[i-1] + c[i]*d[i] + c[i]*e[i]
         *              = b[i-1] + c[i]*(d[i]+e[i]) = b[i-1] + s[i]).
         * Kept sequential: b[i-1] written by the previous iteration
         * must be fully available before b[i] is computed. */
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = b[i-1] + s[i];
        }

        /* Pass 3: a[i] = b[i-1] + c[i]*d[i]. All of b has already been
         * written by pass 2 above (that loop fully completed before this
         * one starts), so reading b[i-1] here is safe and each iteration
         * writes a distinct a[i] -- independent across i. */
        #pragma omp parallel for default(none) shared(a, b, c, d)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(s);
    return (real_t)0;
}
