#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* The original a[i+1] write here is overwritten by the next
         * iteration's a[i] write for all i < LEN_1D-2, so it is dead
         * except at the very last iteration. Dropping it removes the
         * cross-iteration dependence; the boundary element LEN_1D-1 is
         * fixed up separately below, after the loop (and hence after
         * b[LEN_1D-2] has its final value). */
        #pragma omp parallel for shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
