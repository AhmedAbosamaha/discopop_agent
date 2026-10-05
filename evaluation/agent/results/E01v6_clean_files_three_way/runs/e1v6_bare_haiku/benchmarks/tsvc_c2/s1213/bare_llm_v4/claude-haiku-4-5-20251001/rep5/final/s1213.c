#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* First loop: compute all a[i] values in parallel
         * Loop-independent: each iteration i writes a[i], reads b[i-1] and c[i].
         * b is not written in this loop, so no loop-carried dependence.
         * Variables: i (loop variable, implicit private), a/b/c/d/e (shared global pointers)
         */
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }

        /* Second loop: compute all b[i] values in parallel
         * Loop-independent: each iteration i writes b[i], reads a[i+1] and d[i].
         * a is not written in this loop (it was finalized in first loop), so no loop-carried dependence.
         * The implicit barrier after the first loop ensures a values are complete before this loop reads them.
         * Variables: i (loop variable, implicit private), a/b/c/d/e (shared global pointers)
         */
        #pragma omp parallel for
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
