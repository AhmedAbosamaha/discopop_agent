#include "data.h"

real_t kernel_s127(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original code kept a running index j, incremented twice per
         * iteration of i (j = -1 initially).  That makes j a simple
         * affine function of i: after processing index i, the two
         * writes land at a[2*i] and a[2*i+1].  Re-deriving that closed
         * form removes the loop-carried dependence on j entirely, so
         * each iteration of i only touches its own two slots of a and
         * can run independently.
         */
        #pragma omp parallel for shared(a, b, c, d, e) schedule(static)
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i + 1] = b[i] + d[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
