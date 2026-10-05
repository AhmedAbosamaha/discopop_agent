#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* The original write to a[i+1] in iteration i is overwritten
         * (never read) by iteration i+1, except for the last iteration.
         * So the loop body reduces to two independent per-element
         * updates, and the surviving a[LEN_1D-1] write is done after. */
#pragma omp parallel for default(none) shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
